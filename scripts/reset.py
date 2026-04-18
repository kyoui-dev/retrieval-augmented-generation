from src.utils import get_connection


def reset():
    conn = get_connection()
    conn.execute(
        """
        DROP TABLE IF EXISTS child_chunks;
        DROP TABLE IF EXISTS parent_chunks;
        DROP EXTENSION IF EXISTS vector;
        """
    )
    conn.close()


if __name__ == "__main__":
    reset()