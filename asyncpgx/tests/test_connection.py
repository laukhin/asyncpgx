"""Test `connection` module."""
import pytest

from asyncpgx import connection as connection_module


@pytest.mark.asyncio
async def test_named_execute_with_named_parameters(postgres_connection: connection_module.ConnectionX):
    """Test `named_execute` method with named parameters."""
    await postgres_connection.named_execute(
        'INSERT INTO test(id, test_1, test_2) VALUES (:id, :test_1, :test_2);', {'id': 1, 'test_1': '1', 'test_2': '2'}
    )
    fetch_result = await postgres_connection.fetchrow('SELECT id, test_1, test_2 FROM test WHERE id=1;')

    assert fetch_result['id'] == 1
    assert fetch_result['test_1'] == '1'
    assert fetch_result['test_2'] == '2'


@pytest.mark.asyncio
async def test_named_executemany_with_named_parameters(postgres_connection: connection_module.ConnectionX):
    """Test `named_executemany` method with named parameters."""
    await postgres_connection.named_executemany(
        'INSERT INTO test(id, test_1, test_2) VALUES (:id, :test_1, :test_2);',
        [
            {'id': 1, 'test_1': '1', 'test_2': '1'},
            {'id': 2, 'test_1': '2', 'test_2': '2'},
            {'id': 3, 'test_1': '3', 'test_2': '3'},
        ],
    )
    fetch_result = await postgres_connection.fetch('SELECT id, test_1, test_2 FROM test ORDER BY id ASC;')

    for i, row in enumerate(fetch_result):
        assert row['id'] == i + 1
        assert row['test_1'] == str(i + 1)
        assert row['test_2'] == str(i + 1)


@pytest.mark.asyncio
async def test_named_fetch_with_named_parameters(postgres_connection: connection_module.ConnectionX):
    """Test `named_fetch` method with named parameters."""
    await postgres_connection.execute(
        '''
        INSERT INTO test(id, test_1, test_2) VALUES (1, '1', '1'),(2, '2', '2'),(3, '3', '3')
        '''
    )

    fetch_result = await postgres_connection.named_fetch('SELECT id, test_1, test_2 FROM test WHERE id=:id;', {'id': 2})

    assert fetch_result[0]['id'] == 2
    assert fetch_result[0]['test_1'] == '2'
    assert fetch_result[0]['test_2'] == '2'


@pytest.mark.asyncio
async def test_named_fetchval_with_named_parameters(postgres_connection: connection_module.ConnectionX):
    """Test `named_fetchval` method with named parameters."""
    await postgres_connection.execute(
        '''
        INSERT INTO test(id, test_1, test_2) VALUES (1, '1', '1'),(2, '2', '2'),(3, '3', '3')
        '''
    )

    fetch_result = await postgres_connection.named_fetchval(
        'SELECT id, test_1, test_2 FROM test WHERE id=:id;', {'id': 2}, column=0
    )

    assert fetch_result == 2


@pytest.mark.asyncio
async def test_named_fetchrow_with_named_parameters(postgres_connection: connection_module.ConnectionX):
    """Test `named_fetchrow` method with named parameters."""
    await postgres_connection.execute(
        '''
        INSERT INTO test(id, test_1, test_2) VALUES (1, '1', '1'),(2, '2', '2'),(3, '3', '3')
        '''
    )

    fetch_result = await postgres_connection.named_fetchrow(
        'SELECT id, test_1, test_2 FROM test WHERE id=:id;',
        {'id': 2},
    )

    assert fetch_result['id'] == 2
