=============
Quickstart
=============

.. code-block:: python

    import asyncpgx

    async def main():
        connection: asyncpgx.ConnectionX = await asyncpgx.connect('postgresql://127.0.0.1:5432')
        # original API stays the same
        await connection.execute('''CREATE TABLE test (id int PRIMARY KEY, test_1 varchar (256), test_2 varchar (256))''')

        # new methods
        await connection.named_execute(
            'INSERT INTO test(id, test_1, test_2) VALUES (:id, :test_1, :test_2);', {'id': 1, 'test_1': '1', 'test_2': '2'}
        )
        await connection.named_executemany(
            'INSERT INTO test(id, test_1, test_2) VALUES (:id, :test_1, :test_2);',
            [
                {'id': 1, 'test_1': '1', 'test_2': '1'},
                {'id': 2, 'test_1': '2', 'test_2': '2'},
                {'id': 3, 'test_1': '3', 'test_2': '3'},
            ],
        )
        await connection.named_fetch('SELECT id, test_1, test_2 FROM test WHERE id=:id;', {'id': 2})
        await connection.named_fetchval('SELECT id, test_1, test_2 FROM test WHERE id=:id;', {'id': 2}, column=0)
        await connection.named_fetchrow(
            'SELECT id, test_1, test_2 FROM test WHERE id=:id;',
            {'id': 2},
        )
