"""Common fixtures."""
import os

import pytest

from asyncpgx import connection as connection_module


POSTGRES_DSN = os.getenv('POSTGRES_TEST_DSN', 'postgresql://127.0.0.1:5432')


@pytest.fixture
async def postgres_connection():
    """Fixture which establishes the connection, creates the test table and
    cleans everything on scope close."""
    connection = await connection_module.connect(POSTGRES_DSN)
    await connection.execute('''CREATE TABLE test (id int PRIMARY KEY, test_1 varchar (256), test_2 varchar (256))''')
    yield connection
    await connection.execute('''DROP TABLE test CASCADE;''')
