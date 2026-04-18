import psycopg
from psycopg import Connection
from pgvector.psycopg import register_vector
from openai import OpenAI
from sentence_transformers import CrossEncoder

from config import DB_CONFIG, EMBEDDING_MODEL_NAME, CROSS_ENCODER_MODEL_NAME


def get_connection() -> Connection:
    conn = psycopg.connect(**DB_CONFIG)
    register_vector(conn)
    return conn


def get_client() -> OpenAI:
    return OpenAI()


def get_embedding(client: OpenAI, text: str) -> list[float]:
    response = client.embeddings.create(
        model=EMBEDDING_MODEL_NAME,
        input=text,
    )
    return response.data[0].embedding


def get_embeddings(client: OpenAI, texts: list[str]) -> list[list[float]]:
    response = client.embeddings.create(
        model=EMBEDDING_MODEL_NAME, 
        input=texts,
    )
    return [item.embedding for item in response.data]


def load_cross_encoder() -> CrossEncoder:
    return CrossEncoder(CROSS_ENCODER_MODEL_NAME)