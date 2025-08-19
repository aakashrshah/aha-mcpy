import json
import logging
from typing import Dict, Any, Optional
from gql import Client, gql
from gql.transport.exceptions import TransportError

try:
    from .aha_types import (
        FEATURE_REF_REGEX, 
        REQUIREMENT_REF_REGEX, 
        NOTE_REF_REGEX,
        Record,
        FeatureResponse,
        RequirementResponse,
        PageResponse,
        SearchResponse,
        Description,
        Page,
        PageChild,
        PageParent,
        SearchDocuments,
        SearchNode
    )
    from .queries import (
        GET_FEATURE_QUERY,
        GET_REQUIREMENT_QUERY,
        GET_PAGE_QUERY,
        SEARCH_DOCUMENTS_QUERY
    )
except ImportError:
    from aha_types import (
        FEATURE_REF_REGEX, 
        REQUIREMENT_REF_REGEX, 
        NOTE_REF_REGEX,
        Record,
        FeatureResponse,
        RequirementResponse,
        PageResponse,
        SearchResponse,
        Description,
        Page,
        PageChild,
        PageParent,
        SearchDocuments,
        SearchNode
    )
    from queries import (
        GET_FEATURE_QUERY,
        GET_REQUIREMENT_QUERY,
        GET_PAGE_QUERY,
        SEARCH_DOCUMENTS_QUERY
    )


logger = logging.getLogger(__name__)


class Handlers:
    def __init__(self, client: Client):
        self.client = client

    def _parse_feature_response(self, data: Dict[str, Any]) -> Optional[Record]:
        """Parse GraphQL response into Feature Record"""
        if not data.get("feature"):
            return None
        
        feature_data = data["feature"]
        return Record(
            name=feature_data["name"],
            description=Description(markdownBody=feature_data["description"]["markdownBody"])
        )

    def _parse_requirement_response(self, data: Dict[str, Any]) -> Optional[Record]:
        """Parse GraphQL response into Requirement Record"""
        if not data.get("requirement"):
            return None
        
        requirement_data = data["requirement"]
        return Record(
            name=requirement_data["name"],
            description=Description(markdownBody=requirement_data["description"]["markdownBody"])
        )

    def _parse_page_response(self, data: Dict[str, Any]) -> Optional[Page]:
        """Parse GraphQL response into Page object"""
        if not data.get("page"):
            return None
        
        page_data = data["page"]
        
        children = [
            PageChild(name=child["name"], referenceNum=child["referenceNum"])
            for child in page_data.get("children", [])
        ]
        
        parent = None
        if page_data.get("parent"):
            parent_data = page_data["parent"]
            parent = PageParent(name=parent_data["name"], referenceNum=parent_data["referenceNum"])
        
        return Page(
            name=page_data["name"],
            description=Description(markdownBody=page_data["description"]["markdownBody"]),
            children=children,
            parent=parent
        )

    def _parse_search_response(self, data: Dict[str, Any]) -> SearchDocuments:
        """Parse GraphQL response into SearchDocuments object"""
        search_data = data["searchDocuments"]
        
        nodes = [
            SearchNode(
                name=node.get("name"),
                url=node["url"],
                searchableId=node["searchableId"],
                searchableType=node["searchableType"]
            )
            for node in search_data["nodes"]
        ]
        
        return SearchDocuments(
            nodes=nodes,
            currentPage=search_data["currentPage"],
            totalCount=search_data["totalCount"],
            totalPages=search_data["totalPages"],
            isLastPage=search_data["isLastPage"]
        )

    async def handle_get_record(self, arguments: Dict[str, Any]) -> str:
        """Handle get_record tool call"""
        reference = arguments.get("reference")
        
        if not reference:
            return "❌ Error: Reference number is required"

        try:
            result: Optional[Record] = None

            if FEATURE_REF_REGEX.match(reference):
                query = gql(GET_FEATURE_QUERY)
                data = await self.client.execute_async(query, variable_values={"id": reference})
                result = self._parse_feature_response(data)
            elif REQUIREMENT_REF_REGEX.match(reference):
                query = gql(GET_REQUIREMENT_QUERY)
                data = await self.client.execute_async(query, variable_values={"id": reference})
                result = self._parse_requirement_response(data)
            else:
                return "❌ Error: Invalid reference number format. Expected DEVELOP-123 or ADT-123-1"

            if not result:
                return f"❌ No record found for reference {reference}"

            return json.dumps({
                "name": result.name,
                "description": {"markdownBody": result.description.markdownBody}
            }, indent=2)
        except TransportError as e:
            logger.error(f"GraphQL Transport Error: {str(e)}")
            return f"❌ Error fetching record: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return f"❌ Error fetching record: {str(e)}"

    async def handle_get_page(self, arguments: Dict[str, Any]) -> str:
        """Handle get_page tool call"""
        reference = arguments.get("reference")
        include_parent = arguments.get("includeParent", False)
        
        if not reference:
            return "❌ Error: Reference number is required"

        if not NOTE_REF_REGEX.match(reference):
            return "❌ Error: Invalid reference number format. Expected ABC-N-213"

        try:
            query = gql(GET_PAGE_QUERY)
            data = await self.client.execute_async(
                query, 
                variable_values={"id": reference, "includeParent": include_parent}
            )

            result = self._parse_page_response(data)

            if not result:
                return f"❌ No page found for reference {reference}"

            page_dict = {
                "name": result.name,
                "description": {"markdownBody": result.description.markdownBody},
                "children": [
                    {"name": child.name, "referenceNum": child.referenceNum}
                    for child in result.children
                ]
            }
            
            if result.parent:
                page_dict["parent"] = {
                    "name": result.parent.name,
                    "referenceNum": result.parent.referenceNum
                }

            return json.dumps(page_dict, indent=2)
        except TransportError as e:
            logger.error(f"GraphQL Transport Error: {str(e)}")
            return f"❌ Error fetching page: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return f"❌ Error fetching page: {str(e)}"

    async def handle_search_documents(self, arguments: Dict[str, Any]) -> str:
        """Handle search_documents tool call"""
        query_text = arguments.get("query")
        searchable_type = arguments.get("searchableType", "Page")
        
        if not query_text:
            return "❌ Error: Search query is required"

        try:
            query = gql(SEARCH_DOCUMENTS_QUERY)
            data = await self.client.execute_async(
                query,
                variable_values={
                    "query": query_text,
                    "searchableType": [searchable_type]
                }
            )

            result = self._parse_search_response(data)

            search_dict = {
                "nodes": [
                    {
                        "name": node.name,
                        "url": node.url,
                        "searchableId": node.searchableId,
                        "searchableType": node.searchableType
                    }
                    for node in result.nodes
                ],
                "currentPage": result.currentPage,
                "totalCount": result.totalCount,
                "totalPages": result.totalPages,
                "isLastPage": result.isLastPage
            }

            return json.dumps(search_dict, indent=2)
        except TransportError as e:
            logger.error(f"GraphQL Transport Error: {str(e)}")
            return f"❌ Error searching documents: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return f"❌ Error searching documents: {str(e)}"
