import uuid

from .models import Document, ParentChunk, ChildChunk


def _compute_page_range(
    start: int,
    end: int,
    boundaries: list[tuple[int, int, int]],
) -> tuple[int, int]:
    pages = [
        page_number
        for s, e, page_number in boundaries
        if s < end and e > start
    ]
    return pages[0], pages[-1]


def split_into_parent_chunks(
    document: Document,
    chunk_size: int = 2000,
    overlap: int = 200,
) -> tuple[list[ParentChunk], list[tuple[int, int, int]]]:
    text = ""
    boundaries = []

    for page in document.pages:
        start = len(text)
        text += page.content
        end = len(text)
        boundaries.append((start, end, page.number))
    
    start = 0
    n = len(text)
    parents = []

    while start < n:
        end = min(start + chunk_size, n)
        content = text[start:end]
        page_start, page_end = _compute_page_range(start, end, boundaries)
        parents.append(
            ParentChunk(
                id=str(uuid.uuid4()),
                content=content,
                offset=start,
                page_start=page_start,
                page_end=page_end,
                document_name=document.name,
            )
        )
        start += chunk_size - overlap

    return parents, boundaries
    


def split_into_child_chunks(
    parent: ParentChunk,
    boundaries: list[tuple[int, int, int]],
    chunk_size: int = 400,
    overlap: int = 50,
) -> list[ChildChunk]:
    text = parent.content
    start = 0
    n = len(text)
    children = []

    while start < n:
        end = min(start + chunk_size, n)
        content = text[start:end]
        abs_start = parent.offset + start
        abs_end = parent.offset + end
        page_start, page_end = _compute_page_range(
            abs_start, 
            abs_end, 
            boundaries,
        )
        children.append(
            ChildChunk(
                id=str(uuid.uuid4()),
                parent_id=parent.id,
                content=content,
                page_start=page_start,
                page_end=page_end,
            )
        )
        start += chunk_size - overlap

    return children