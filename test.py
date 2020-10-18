import asyncpg
import asyncpgx
import asyncio

async def main():
    connection: asyncpgx.ConnectionX = await asyncpgx.connect(
        host='127.0.0.1',
        database='dvdrental',
        user='postgres',
        password='SET56?ra'
    )
    # connection: asyncpgx.ConnectionX = await asyncpgx.connect('postgresql://postgres@ocalhost/dvdrental')
    # original API stays the same
    await connection.execute('''CREATE TABLE test (id int PRIMARY KEY, test_1 varchar (256), test_2 varchar (256))''')

    # new connection methods
    await connection.named_execute(
        'INSERT INTO test(id, test_1, test_2) VALUES (:id, :test_1, :test_2);', {'id': 1, 'test_1': '1'}
        # 'INSERT INTO test(id, test_1, test_2) VALUES (:id, :test_1, :test_2);', {'id': 1, 'test_1': '1', 'test_2': '2'}
    )
    values = await connection.named_fetch('SELECT id, test_1, test_2 FROM test WHERE id=:id;', {'id': 1})
    # values = await connection.named_fetch('SELECT * FROM film WHERE film_id=:film_id;', {'film_id': 133})
    print(values)
    # await connection.close()
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
