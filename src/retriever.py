from typing import Any

from openai import OpenAI
import numpy as np

from .utils import get_connection, get_embedding


def keyword_search(
    query: str, 
    top_k: int = 5, 
) -> list[dict[str, Any]]:
    tsquery = " | ".join(query.split())
    conn = get_connection()
    records = conn.execute(
        """
        WITH q AS (
            SELECT to_tsquery('simple', %s) AS query
        )
        SELECT
            c.id,
            c.content,
            c.page_start,
            c.page_end,
            p.id,
            p.content,
            p.page_start,
            p.page_end,
            p.document_name,
            ts_rank_cd(c.textsearch, q.query, 32) AS score
        FROM child_chunks c
        JOIN parent_chunks p
            ON c.parent_id = p.id
        CROSS JOIN q
        WHERE c.textsearch @@ q.query
        ORDER BY score DESC
        LIMIT %s
        """,
        (tsquery, top_k)
    ).fetchall()
    conn.close()
    return [
        {
            "id": record[0],
            "content": record[1],
            "page_start": record[2],
            "page_end": record[3],
            "parent": {
                "id": record[4],
                "content": record[5],
                "page_start": record[6],
                "page_end": record[7],
            },
            "document_name": record[8],
            "score": record[9],
        }
        for record in records
    ]


def semantic_search(
    query: str,
    client: OpenAI,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    query_embedding = np.array(get_embedding(client, query))
    conn = get_connection()
    records = conn.execute(
        """
        SELECT
            c.id,
            c.content,
            c.page_start,
            c.page_end,
            p.id AS parent_id,
            p.content AS parent_content,
            p.page_start AS parent_page_start,
            p.page_end AS parent_page_end,
            p.document_name,
            c.embedding <#> %s AS distance
        FROM child_chunks c
        JOIN parent_chunks p
          ON c.parent_id = p.id
        ORDER BY c.embedding <#> %s
        LIMIT %s
        """,
        (query_embedding, query_embedding, top_k),
    ).fetchall()
    conn.close()
    return [
        {
            "id": record[0],
            "content": record[1],
            "page_start": record[2],
            "page_end": record[3],
            "parent": {
                "id": record[4],
                "content": record[5],
                "page_start": record[6],
                "page_end": record[7],
            },
            "document_name": record[8],
            "distance": record[9],
        }
        for record in records
    ]


def hybrid_search(
    query: str,
    client: OpenAI,
    candidate_k: int = 20,
    rrf_k: int = 60,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    tsquery = " | ".join(query.split())
    query_embedding = np.array(get_embedding(client, query))
    conn = get_connection()
    records = conn.execute(
        """
        WITH keyword_search AS (
            SELECT
                id,
                ROW_NUMBER() OVER (ORDER BY score DESC) AS rank
            FROM (
                SELECT
                    c.id,
                    ts_rank_cd(c.textsearch, q.query, 32) AS score
                FROM child_chunks c
                CROSS JOIN (
                    SELECT to_tsquery('simple', %s) AS query
                ) q
                WHERE c.textsearch @@ q.query
                ORDER BY score DESC
                LIMIT %s
            ) t
        ),
        semantic_search AS (
            SELECT
                id,
                ROW_NUMBER() OVER (ORDER BY score ASC) AS rank
            FROM (
                SELECT
                    c.id,
                    c.embedding <#> %s AS score
                FROM child_chunks c
                ORDER BY c.embedding <#> %s
                LIMIT %s
            ) t
        ),
        rrf AS (
            SELECT
                COALESCE(k.id, s.id) AS id,
                COALESCE(1.0 / (%s + k.rank), 0.0) +
                COALESCE(1.0 / (%s + s.rank), 0.0) AS score
            FROM keyword_search k
            FULL OUTER JOIN semantic_search s
                ON k.id = s.id
        )
        SELECT
            c.id,
            c.content,
            c.page_start,
            c.page_end,
            p.id,
            p.content,
            p.page_start,
            p.page_end,
            p.document_name,
            rrf.score
        FROM rrf
        JOIN child_chunks c
            ON rrf.id = c.id
        JOIN parent_chunks p
            ON c.parent_id = p.id
        ORDER BY rrf.score DESC
        LIMIT %s
        """,
        (
            tsquery,
            candidate_k,
            query_embedding,
            query_embedding,
            candidate_k,
            rrf_k,
            rrf_k,
            top_k,
        )
    ).fetchall()
    conn.close()
    return [
        {
            "id": record[0],
            "content": record[1],
            "page_start": record[2],
            "page_end": record[3],
            "parent": {
                "id": record[4],
                "content": record[5],
                "page_start": record[6],
                "page_end": record[7],
            },
            "document_name": record[8],
            "score": record[9],
        }
        for record in records
    ]