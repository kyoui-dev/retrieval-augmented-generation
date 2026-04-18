from pathlib import Path

from src.parser import parse_pdf
from src.chunker import split_into_parent_chunks, split_into_child_chunks
from src.utils import get_connection, get_client, get_embeddings


def ingest(file_path):
    document = parse_pdf(file_path)
    parents, boundaries = split_into_parent_chunks(document)
    conn = get_connection()
    client = get_client()

    for parent in parents:
        children = split_into_child_chunks(parent, boundaries)
        conn.execute(
            """
            INSERT INTO parent_chunks (
                id, 
                content, 
                "offset", 
                page_start, 
                page_end,
                document_name
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
            """,
            (
                parent.id,
                parent.content,
                parent.offset,
                parent.page_start,
                parent.page_end,
                parent.document_name,
            ),
        )
        embeddings = get_embeddings(client, [c.content for c in children])

        for child, embedding in zip(children, embeddings):
            conn.execute(
                """
                INSERT INTO child_chunks (
                    id, 
                    parent_id, 
                    content, 
                    page_start, 
                    page_end, 
                    embedding
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (
                    child.id, 
                    child.parent_id, 
                    child.content, 
                    child.page_start, 
                    child.page_end, 
                    embedding,
                )
            )
    
        conn.commit()

    conn.close()


if __name__ == "__main__":
    for file_path in Path("./data").glob("*.pdf"):
        ingest(str(file_path))