"""Module with extensions of asyncpg `Connection` class."""
import functools
import typing

import asyncpg
from asyncpg import cursor

from asyncpgx import prepared_statement
from asyncpgx import query as query_module


class ConnectionX(asyncpg.connection.Connection):
    """Extended version of asyncpg `Connection` class.

    Provides various extension methods, but doesn't touches the original
    ones
    """

    def _prepare_asyncpg_parameters(
        self, query: str, args: typing.Any, converter: query_module.QueryParamsConverter
    ) -> typing.Tuple[str, typing.List]:
        """Prepare high-level query and arguments to underlying asyncpg
        backend."""
        converted_query, params_order_list = query_module.construct_asyncpg_query(query)
        return converted_query, converter.prepare_asyncpg_args(args, params_order_list)

    async def named_execute(self, query: str, args: typing.Dict, timeout: typing.Optional[float] = None) -> str:
        """Extended versions of `execute` with support of the named
        parameters."""
        # Convert the received query in the parameter to all lower-case
        query = query.lower()
        # Fetch the column string that is passed as part of INTO clause
        query_columns = query.split('into')[1].split('values')[0].strip()
        # Convert the column into list for further detailed logging
        columns = [column.strip() for column in query_columns[query_columns.index('(') + 1:-1].split(',')]

        number_of_columns = len(columns)
        number_of_values = len(list(args.keys()))

        missing_columns = set(columns) - set(args.keys())

        # Scenario: When the value passed in parameter do not match the number of columns
        if number_of_values < number_of_columns:
            raise KeyError('Values missing. Columns that are missing values: {0}'.format(missing_columns))
        # Scenario: When the expected column id is not received
        if 'id' not in args:
            raise KeyError('Expected column name-> id :: Provided column name-> {}'.format(list(args.keys())[0]))

        converted_query, asyncpg_args = self._prepare_asyncpg_parameters(
            query, args, query_module.QueryParamsDictConverter()
        )
        return await super().execute(converted_query, *asyncpg_args, timeout=timeout)

    async def named_executemany(self, query: str, args: typing.List, *, timeout: typing.Optional[float] = None) -> None:
        """Extended versions of `executemany` with support of the named
        parameters."""
        converted_query, asyncpg_args = self._prepare_asyncpg_parameters(
            query, args, query_module.QueryParamsListDictConverter()
        )
        return await super().executemany(converted_query, asyncpg_args, timeout=timeout)

    async def named_fetch(
        self, query: str, args: typing.Dict, timeout: typing.Optional[float] = None
    ) -> typing.List[asyncpg.Record]:
        """Extended versions of `fetch` with support of the named
        parameters."""
        converted_query, asyncpg_args = self._prepare_asyncpg_parameters(
            query, args, query_module.QueryParamsDictConverter()
        )
        return await super().fetch(converted_query, *asyncpg_args, timeout=timeout)

    async def named_fetchval(
        self, query: str, args: typing.Dict, column: int = 0, timeout: typing.Optional[float] = None
    ) -> typing.Optional[typing.Any]:
        """Extended versions of `fetchval` with support of the named
        parameters."""
        converted_query, asyncpg_args = self._prepare_asyncpg_parameters(
            query, args, query_module.QueryParamsDictConverter()
        )
        return await super().fetchval(converted_query, *asyncpg_args, column=column, timeout=timeout)

    async def named_fetchrow(
        self, query: str, args: typing.Dict, timeout: typing.Optional[float] = None
    ) -> typing.Optional[asyncpg.Record]:
        """Extended versions of `fetchrow` with support of the named
        parameters."""
        converted_query, asyncpg_args = self._prepare_asyncpg_parameters(
            query, args, query_module.QueryParamsDictConverter()
        )
        return await super().fetchrow(converted_query, *asyncpg_args, timeout=timeout)

    def named_cursor(
        self,
        query: str,
        args: typing.Dict,
        prefetch: typing.Optional[int] = None,
        timeout: typing.Optional[float] = None,
    ) -> cursor.CursorFactory:
        """Extended version of `cursor` with support of the named
        parameters."""
        converted_query, asyncpg_args = self._prepare_asyncpg_parameters(
            query, args, query_module.QueryParamsDictConverter()
        )
        return super().cursor(converted_query, *asyncpg_args, prefetch=prefetch, timeout=timeout)

    async def named_prepare(
        self, query: str, *, timeout: typing.Optional[float] = None
    ) -> prepared_statement.PreparedStatementX:
        """Extended version of `prepare` with support of the named
        parameters."""
        converted_query, params_order_list = query_module.construct_asyncpg_query(query)
        self._check_open()
        stmt = await self._get_statement(converted_query, timeout, named=True, use_cache=False)
        return prepared_statement.PreparedStatementX(self, converted_query, stmt, query, params_order_list)


create_pool = functools.partial(asyncpg.create_pool, connection_class=ConnectionX)
connect = functools.partial(asyncpg.connect, connection_class=ConnectionX)
