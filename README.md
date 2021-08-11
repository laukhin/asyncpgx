# asyncpgx
[![Build passed](https://img.shields.io/github/workflow/status/laukhin/asyncpgx/CI)](https://github.com/laukhin/asyncpgx/actions?query=workflow%3ACI)
[![Test coverage](https://img.shields.io/codecov/c/github/laukhin/asyncpgx)](https://codecov.io/gh/laukhin/asyncpgx)
[![Version](https://img.shields.io/pypi/v/asyncpgx)](https://pypi.org/project/asyncpgx/)

Extensions for asyncpg.

Based on the [asyncpg](https://github.com/MagicStack/asyncpg) and highly inspired by the [sqlx](https://github.com/jmoiron/sqlx) package

This package supports 3.6+ python versions

## Setup
Use `pip install asyncpgx`

## Purpose
This is a thin wrapper on the `asyncpg` package.
Our purpose is to provide convenient extensions to the original package.
We're trying to delegate as much work as we can to the asyncpg (basically our extension methods are high-level proxies to the underlying ones)
and make only converting job.
Original asyncpg API stays the same, you can see it in the [asyncpg documentation](https://magicstack.github.io/asyncpg/current/).

## Functionality
* queries with named parameters, i.e.
```python
import asyncpgx

connection = await asyncpgx.connect('postgresql://127.0.0.1:5432')
await connection.named_fetch('''SELECT field FROM some_table WHERE id <= :id;''', {'id': 1})
```
* prepared statements with named parameters, i.e.
```python
import asyncpgx

connection = await asyncpgx.connect('postgresql://127.0.0.1:5432')
prepared_statement = await connection.named_prepare('''SELECT field FROM some_table WHERE id <= :id;''')
await prepared_statement.named_fetch({'id': 1})
```

## Documentation
You can find project documentation [here](https://laukhin.github.io/asyncpgx/index.html)

## Changelog
You can find all releases description [here](https://github.com/laukhin/asyncpgx/releases)
