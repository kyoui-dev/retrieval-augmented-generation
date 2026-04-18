from dataclasses import dataclass, field


@dataclass
class Page:
    content: str
    number: int


@dataclass
class Document:
    name: str
    pages: list[Page] = field(default_factory=list)


@dataclass
class ParentChunk:
    id: str
    content: str
    offset: int
    page_start: int
    page_end: int
    document_name: str


@dataclass
class ChildChunk:
    id: str
    parent_id: str
    content: str
    page_start: int
    page_end: int
    embedding: list[float] | None = None