from src.utils import get_connection


def setup():
    conn = get_connection()
    conn.execute("""
        CREATE EXTENSION IF NOT EXISTS vector;
                 
        CREATE TABLE IF NOT EXISTS parent_chunks (
            id UUID PRIMARY KEY,
            content TEXT NOT NULL,
            "offset" INTEGER NOT NULL,
            page_start INTEGER NOT NULL,
            page_end INTEGER NOT NULL,
            document_name TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS child_chunks (
            id UUID PRIMARY KEY,
            parent_id UUID NOT NULL REFERENCES parent_chunks(id),
            content TEXT NOT NULL,
            page_start INTEGER NOT NULL,
            page_end INTEGER NOT NULL,
            textsearch tsvector GENERATED ALWAYS AS (
                to_tsvector('simple', coalesce(content, ''))
            ) STORED,
            embedding vector(1536) NOT NULL
        );
                 
        CREATE INDEX IF NOT EXISTS child_chunks_textsearch_idx
        ON child_chunks
        USING gin (textsearch);

        CREATE INDEX IF NOT EXISTS child_chunks_embedding_idx
        ON child_chunks
        USING hnsw (embedding vector_ip_ops);
    """)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    setup()