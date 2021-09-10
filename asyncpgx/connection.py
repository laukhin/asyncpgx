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
        """Extended versions of `execute` with support of the named parameters.

        :param query: SQL query to execute (could include named parameters).
        :param args: Dict with the parameters values.
        :param timeout: Optional timeout value in seconds.
        """
        converted_query, asyncpg_args = self._prepare_asyncpg_parameters(
            query, args, query_module.QueryParamsDictConverter()
        )
        query_result: str = await super().execute(converted_query, *asyncpg_args, timeout=timeout)
        return query_result

    async def named_executemany(self, query: str, args: typing.List, *, timeout: typing.Optional[float] = None) -> None:
        """Extended versions of `executemany` with support of the named
        parameters.

        :param query: SQL query to execute (could include named parameters).
        :param args: List of dicts with the parameters values.
        :param timeout: Optional timeout value in seconds.
        """
        converted_query, asyncpg_args = self._prepare_asyncpg_parameters(
            query, args, query_module.QueryParamsListDictConverter()
        )
        query_result: None = await super().executemany(converted_query, asyncpg_args, timeout=timeout)
        return query_result

    async def named_fetch(
        self, query: str, args: typing.Dict, timeout: typing.Optional[float] = None
    ) -> typing.List[asyncpg.Record]:
        """Extended versions of `fetch` with support of the named parameters.

        :param query: SQL query to execute (could include named parameters).
        :param args: Dict with the parameters values.
        :param timeout: Optional timeout value in seconds.
        """
        converted_query, asyncpg_args = self._prepare_asyncpg_parameters(
            query, args, query_module.QueryParamsDictConverter()
        )
        query_result: typing.List[asyncpg.Record] = await super().fetch(converted_query, *asyncpg_args, timeout=timeout)
        return query_result

    async def named_fetchval(
        self, query: str, args: typing.Dict, column: int = 0, timeout: typing.Optional[float] = None
    ) -> typing.Optional[typing.Any]:
        """Extended versions of `fetchval` with support of the named
        parameters.

        :param query: SQL query to execute (could include named parameters).
        :param args: Dict with the parameters values.
        :param column: Numeric index within the record of the value to return.
        :param timeout: Optional timeout value in seconds.
        """
        converted_query, asyncpg_args = self._prepare_asyncpg_parameters(
            query, args, query_module.QueryParamsDictConverter()
        )
        return await super().fetchval(converted_query, *asyncpg_args, column=column, timeout=timeout)

    async def named_fetchrow(
        self, query: str, args: typing.Dict, timeout: typing.Optional[float] = None
    ) -> typing.Optional[asyncpg.Record]:
        """Extended versions of `fetchrow` with support of the named
        parameters.

        :param query: SQL query to execute (could include named parameters).
        :param args: Dict with the parameters values.
        :param timeout: Optional timeout value in seconds.
        """
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
        """Extended version of `cursor` with support of the named parameters.

        :param query: SQL query to execute (could include named parameters).
        :param args: Dict with the parameters values.
        :param prefetch: The number of rows the *cursor iterator* will prefetch (defaults to ``50``.)
        :param timeout: Optional timeout value in seconds.
        """
        converted_query, asyncpg_args = self._prepare_asyncpg_parameters(
            query, args, query_module.QueryParamsDictConverter()
        )
        return super().cursor(converted_query, *asyncpg_args, prefetch=prefetch, timeout=timeout)

    async def named_prepare(
        self, query: str, *, timeout: typing.Optional[float] = None
    ) -> prepared_statement.PreparedStatementX:
        """Extended version of `prepare` with support of the named parameters.

        :param query: SQL query to execute (could include named parameters).
        :param timeout: Optional timeout value in seconds.
        """
        converted_query, params_order_list = query_module.construct_asyncpg_query(query)
        self._check_open()
        stmt = await self._get_statement(converted_query, timeout, named=True, use_cache=False)
        return prepared_statement.PreparedStatementX(self, converted_query, stmt, query, params_order_list)


create_pool = functools.partial(asyncpg.create_pool, connection_class=ConnectionX)
connect = functools.partial(asyncpg.connect, connection_class=ConnectionX)
