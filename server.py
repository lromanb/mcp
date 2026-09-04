from mcp.server.mcpserver import MCPServer
from connection import get_conn

server = MCPServer(
    name="Calculator Server",
    version="1.0.0"
)


@server.tool()
def hello(name: str) -> str:
    """Say hello."""
    return f"Hello, {name}!"


@server.tool()
def add(a: int, b: int) -> int:
    """add two integers."""
    return a + b


@server.tool()
def check_postgresql_query(query: str) -> dict:
    """
    Execute PostgreSQL SQL in a read-only transaction.

    Returns OK if PostgreSQL accepts the query,
    otherwise returns the PostgreSQL error.
    """

    if not query.strip():
        return {
            "status": "ERROR",
            "error": "Query is empty."
        }

    try:
        with get_conn() as conn:

            with conn.transaction():

                with conn.cursor() as cur:

                    cur.execute(
                        "SET LOCAL statement_timeout = '5000ms'"
                    )

                    cur.execute(
                        "SET TRANSACTION READ ONLY"
                    )

                    cur.execute(query)

                    return {
                        "status": "OK",
                        "row_count": cur.rowcount
                    }

    except Exception as e:

        return {
            "status": "ERROR",
            "error": str(e)
        }


if __name__ == "__main__":
    server.run()