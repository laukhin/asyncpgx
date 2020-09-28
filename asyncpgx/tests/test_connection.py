"""Test `connection` module."""
import pytest

from asyncpgx import connection as connection_module


@pytest.mark.asyncio
async def test_executex_with_named_parameters(postgres_connection: connection_module.XConnection):
    """Test `executex` method with named parameters."""
    await postgres_connection.executex(
        'INSERT INTO test(id, test_1, test_2) VALUES (:id, :test_1, :test_2);', {'id': 1, 'test_1': '1', 'test_2': '2'}
    )
    fetch_result = await postgres_connection.fetchrow('SELECT id, test_1, test_2 FROM test WHERE id=1;')

    assert fetch_result['id'] == 1
    assert fetch_result['test_1'] == '1'
    assert fetch_result['test_2'] == '2'
