"""Common fixtures."""
import os

import pytest

from asyncpgx import connection as connection_module


POSTGRESQL_DSN: str = os.getenv('POSTGRESQL_TEST_DSN', 'postgresql://127.0.0.1:5432')


@pytest.fixture
async def postgres_connection() -> connection_module.XConnection:  # type: ignore
    """Fixture which establishes the connection, creates the test table and
    cleans everything on scope close."""
    connection: connection_module.XConnection = await connection_module.connect('postgresql://127.0.0.1:5432')
    await connection.execute('''CREATE TABLE test (id int PRIMARY KEY, test_1 varchar (256), test_2 varchar (256))''')
    yield connection
    await connection.execute('''DROP TABLE test CASCADE;''')
