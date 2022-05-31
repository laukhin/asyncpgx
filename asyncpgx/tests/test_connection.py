"""Test `connection` module."""
import pytest

from asyncpgx import connection as connection_module
from asyncpgx import exceptions


@pytest.mark.asyncio
async def test_named_execute_with_named_parameters(postgres_connection: connection_module.ConnectionX) -> None:
    """Test `named_execute` method with named parameters."""
    await postgres_connection.named_execute(
        'INSERT INTO test(id, test_1, test_2) VALUES (:id, :test_1, :test_2);', {'id': 1, 'test_1': '1', 'test_2': '2'}
    )
    fetch_result = await postgres_connection.fetchrow('SELECT id, test_1, test_2 FROM test WHERE id=1;')

    assert fetch_result['id'] == 1
    assert fetch_result['test_1'] == '1'
    assert fetch_result['test_2'] == '2'


@pytest.mark.asyncio
async def test_named_executemany_with_named_parameters(postgres_connection: connection_module.ConnectionX) -> None:
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
async def test_named_fetch_with_named_parameters(postgres_connection: connection_module.ConnectionX) -> None:
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
async def test_named_fetchval_with_named_parameters(postgres_connection: connection_module.ConnectionX) -> None:
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
async def test_named_fetchrow_with_named_parameters(postgres_connection: connection_module.ConnectionX) -> None:
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

    assert fetch_result and fetch_result['id'] == 2


@pytest.mark.asyncio
async def test_named_cursor_with_named_parameters(postgres_connection: connection_module.ConnectionX) -> None:
    """Test `named_cursor` method with named parameters."""
    await postgres_connection.execute(
        '''
        INSERT INTO test(id, test_1, test_2) VALUES (1, '1', '1'),(2, '2', '2'),(3, '2', '3')
        '''
    )

    async with postgres_connection.transaction():
        async for row in postgres_connection.named_cursor(
            'SELECT id, test_1, test_2 FROM test WHERE test_1=:test_1', {'test_1': '2'}
        ):
            assert row['test_1'] == '2'
            assert row['id'] in {2, 3}


@pytest.mark.asyncio
async def test_named_prepare_cursor_with_named_parameters(postgres_connection: connection_module.ConnectionX) -> None:
    """Test `named_prepare` with `named_cursor` method with named
    parameters."""
    await postgres_connection.execute(
        '''INSERT INTO test (id, test_1, test_2) VALUES (1, '1', '3'),
                                                        (2, '2', '4'),
                                                        (3, '2', '5')'''
    )

    prepared_statement = await postgres_connection.named_prepare(
        '''SELECT id, test_1, test_2 FROM test WHERE test_1=:test_1;'''
    )

    async with postgres_connection.transaction():
        async for row in prepared_statement.named_cursor({'test_1': '2'}):
            assert row['test_1'] == '2'
            assert row['id'] in {2, 3}


@pytest.mark.asyncio
async def test_named_prepare_fetch_with_named_parameters(postgres_connection: connection_module.ConnectionX) -> None:
    """Test `named_prepare` with `named_fetch` method with named parameters."""
    await postgres_connection.execute('''INSERT INTO test (id, test_1, test_2) VALUES (1, '2', '3')''')
    prepared_statement = await postgres_connection.named_prepare(
        '''SELECT id, test_1, test_2 FROM test WHERE id=:id;'''
    )

    query_result = await prepared_statement.named_fetch({'id': 1})

    assert query_result[0]['id'] == 1
    assert query_result[0]['test_1'] == '2'
    assert query_result[0]['test_2'] == '3'


@pytest.mark.asyncio
async def test_named_prepare_fetchval_with_named_parameters(postgres_connection: connection_module.ConnectionX) -> None:
    """Test `named_prepare` with `named_fetchval` method with named
    parameters."""
    await postgres_connection.execute('''INSERT INTO test (id, test_1, test_2) VALUES (1, '2', '3'), (2, '4', '5')''')
    prepared_statement = await postgres_connection.named_prepare(
        '''SELECT id, test_1, test_2 FROM test WHERE id=:id;'''
    )

    query_result = await prepared_statement.named_fetchval({'id': 2}, column=1)

    assert query_result == '4'


@pytest.mark.asyncio
async def test_named_prepare_fetchrow_with_named_parameters(postgres_connection: connection_module.ConnectionX) -> None:
    """Test `named_prepare` with `named_fetchrow` method with named
    parameters."""
    await postgres_connection.execute('''INSERT INTO test (id, test_1, test_2) VALUES (1, '2', '3'), (2, '4', '5')''')
    prepared_statement = await postgres_connection.named_prepare(
        '''SELECT id, test_1, test_2 FROM test WHERE id=:id;'''
    )

    query_result = await prepared_statement.named_fetchrow({'id': 2})

    assert query_result['id'] == 2
    assert query_result['test_1'] == '4'
    assert query_result['test_2'] == '5'


@pytest.mark.asyncio
async def test_missing_arguments(postgres_connection: connection_module.ConnectionX) -> None:
    """Test missing arguments exception."""
    with pytest.raises(exceptions.MissingRequiredArgumentError):
        await postgres_connection.named_execute(
            '''SELECT id, test_1, test_2 FROM test WHERE id=:id AND test_1=:test_1;''', {'id': 1}
        )


@pytest.mark.asyncio
async def test_unused_arguments(postgres_connection: connection_module.ConnectionX) -> None:
    """Test unused arguments exception."""
    with pytest.raises(exceptions.UnusedArgumentsError):
        await postgres_connection.named_execute(
            '''SELECT id, test_1, test_2 FROM test WHERE id=:id;''', {'id': 1, 'test_1': '2'}
        )


@pytest.mark.asyncio
async def test_missing_arguments_list(postgres_connection: connection_module.ConnectionX) -> None:
    """Test missing arguments exception with list of params."""
    with pytest.raises(exceptions.MissingRequiredArgumentError):
        await postgres_connection.named_executemany(
            '''SELECT id, test_1, test_2 FROM test WHERE id=:id AND test_1=:test_1;''', [{'id': 1}, {'id': 2}]
        )


@pytest.mark.asyncio
async def test_unused_arguments_list(postgres_connection: connection_module.ConnectionX) -> None:
    """Test unused arguments exception with list of params."""
    with pytest.raises(exceptions.UnusedArgumentsError):
        await postgres_connection.named_executemany(
            '''SELECT id, test_1, test_2 FROM test WHERE id=:id;''',
            [{'id': 1, 'test_1': '2'}, {'id': 2, 'test_1': '3'}],
        )
