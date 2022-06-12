import dataclasses
from typing import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy_utils import create_database, database_exists  # type: ignore

from models.base import Base, get_postgres_url


@dataclasses.dataclass
class DBSetting:
    port: str = "5432"
    database: str = "test"
    encoding: str = "utf-8"
    echo: bool = False


def pytest_addoption(parser: pytest.Parser):
    """
    コマンドライン上でテストデータベースの設定の上書きができるようにします。
    """
    parser.addoption("--port", action="store", default="5432")
    parser.addoption("--database", action="store", default="test")
    parser.addoption("--encoding", action="store", default="utf-8")
    parser.addoption("--echo", action="store_true")


@pytest.fixture(scope="session")
def db_setting(request: pytest.FixtureRequest) -> DBSetting:
    return DBSetting(
        port=request.config.getoption("--port"),
        database=request.config.getoption("--database"),
        encoding=request.config.getoption("--encoding"),
        echo=request.config.getoption("--echo"),
    )


@pytest.fixture(scope="session")
def connection(db_setting: DBSetting) -> Connection:
    """
    test sessionが開始されると、connectionを作ります。
    test用のデータベースがなければ作成したあと接続します。
    """
    TEST_SQLALCHEMY_DATABASE_URL = get_postgres_url(
        port=db_setting.port, database=db_setting.database
    )
    engine = create_engine(
        TEST_SQLALCHEMY_DATABASE_URL, encoding=db_setting.encoding, echo=db_setting.echo
    )

    if not database_exists(TEST_SQLALCHEMY_DATABASE_URL):
        create_database(TEST_SQLALCHEMY_DATABASE_URL)

    return engine.connect()


@pytest.fixture(scope="session")
def testdb(connection: Connection) -> Generator[None, None, None]:
    """
    test sessionが開始されると、メタデータ上にあるテーブルの作成を行います。
    test sessionが終了すると、作成されたテーブルをすべて削除します。
    """
    Base.metadata.bind = connection
    connection.execute("SET CONSTRAINTS ALL DEFERRED;")
    Base.metadata.create_all()

    yield

    Base.metadata.drop_all()
    connection.execute("SET CONSTRAINTS ALL IMMEDIATE;")


@pytest.fixture(scope="function")
def test_session(
    testdb, connection: Connection
) -> Generator[scoped_session, None, None]:
    """
    各テストが開始されるたびにセッションを作成します。
    テストが終了するとロールバックします。
    """
    transaction = connection.begin()
    yield scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=connection)
    )
    transaction.rollback()
