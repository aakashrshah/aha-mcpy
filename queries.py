"""GraphQL queries for Aha! API"""

GET_PAGE_QUERY = """
query GetPage($id: ID!, $includeParent: Boolean!) {
  page(id: $id) {
    name
    description {
      markdownBody
    }
    children {
      name
      referenceNum
    }
    parent @include(if: $includeParent) {
      name
      referenceNum
    }
  }
}
"""

GET_FEATURE_QUERY = """
query GetFeature($id: ID!) {
  feature(id: $id) {
    name
    description {
      markdownBody
    }
  }
}
"""

GET_REQUIREMENT_QUERY = """
query GetRequirement($id: ID!) {
  requirement(id: $id) {
    name
    description {
      markdownBody
    }
  }
}
"""

SEARCH_DOCUMENTS_QUERY = """
query SearchDocuments($query: String!, $searchableType: [String!]!) {
  searchDocuments(filters: {query: $query, searchableType: $searchableType}) {
    nodes {
      name
      url
      searchableId
      searchableType
    }
    currentPage
    totalCount
    totalPages
    isLastPage
  }
}
"""
