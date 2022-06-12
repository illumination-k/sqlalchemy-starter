from sqlalchemy import event
from sqlalchemy.engine import Connection
from sqlalchemy.ext.declarative import declarative_base


def get_postgres_url(database: str = "main", port: str = "5432") -> str:
    return f"postgresql://postgres:postgres@localhost:{port}/{database}"


Base = declarative_base()


class QueryCounter:
    """
    Queryの数をカウントできるようにする
    https://stackoverflow.com/questions/19073099/how-to-count-sqlalchemy-queries-in-unit-tests
    """

    def __init__(self, connection: Connection) -> None:
        self.engine = connection.engine
        self.count = 0

    def callback(self, *args, **kwargs):
        self.count += 1

    def __enter__(self):
        event.listen(self.engine, "before_cursor_execute", self.callback)
        return self

    def __exit__(self, *args, **kwargs):
        event.remove(self.engine, "before_cursor_execute", self.callback)
