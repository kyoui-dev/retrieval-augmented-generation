from dataclasses import dataclass, field


@dataclass
class Page:
    content: str
    number: int


@dataclass
class Document:
    name: str
    pages: list[Page] = field(default_factory=list)