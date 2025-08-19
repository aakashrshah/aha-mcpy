import re
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class Description:
    markdownBody: str


@dataclass
class Record:
    name: str
    description: Description


@dataclass
class FeatureResponse:
    feature: Record


@dataclass
class RequirementResponse:
    requirement: Record


@dataclass
class PageChild:
    name: str
    referenceNum: str


@dataclass
class PageParent:
    name: str
    referenceNum: str


@dataclass
class Page:
    name: str
    description: Description
    children: List[PageChild]
    parent: Optional[PageParent] = None


@dataclass
class PageResponse:
    page: Page


@dataclass
class SearchNode:
    name: Optional[str]
    url: str
    searchableId: str
    searchableType: str


@dataclass
class SearchDocuments:
    nodes: List[SearchNode]
    currentPage: int
    totalCount: int
    totalPages: int
    isLastPage: bool


@dataclass
class SearchResponse:
    searchDocuments: SearchDocuments


# Regular expressions for validating reference numbers
FEATURE_REF_REGEX = re.compile(r'^([A-Z][A-Z0-9]*)-(\d+)$')
REQUIREMENT_REF_REGEX = re.compile(r'^([A-Z][A-Z0-9]*)-(\d+)-(\d+)$')
NOTE_REF_REGEX = re.compile(r'^([A-Z][A-Z0-9]*)-N-(\d+)$')
