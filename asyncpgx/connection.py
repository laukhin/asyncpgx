"""Module with extensions of asyncpg `Connection` class."""
import typing

import asyncpg

from asyncpgx import query as query_module


class XConnection(asyncpg.connection.Connection):
    """Extended version of asyncpg `Connection` class.

    Provides various extension methods, but doesn't touches the original
    ones
    """

    def _prepare_asyncpg_parameters(self, query: str, args: typing.Any, converter: query_module.QueryParamsConverter):
        """Prepare high-level query and arguments to underlying asyncpg
        backend."""
        converted_query, params_order_list = converter.construct_asyncpg_query(query)
        return converted_query, converter.prepare_asyncpg_args(args, params_order_list)

    async def executex(self, query: str, args: typing.Dict, timeout: typing.Optional[float] = None) -> str:
        """Extended versions of `execute` with support of the named
        parameters."""
        converted_query, asyncpg_args = self._prepare_asyncpg_parameters(
            query, args, query_module.QueryParamsDictConverter()
        )
        return await super().execute(converted_query, *asyncpg_args, timeout=timeout)

    async def executemanyx(self, query: str, args: typing.List, *, timeout: typing.Optional[float] = None):
        """Extended versions of `executemany` with support of the named
        parameters."""
        converted_query, asyncpg_args = self._prepare_asyncpg_parameters(
            query, args, query_module.QueryParamsListDictConverter()
        )
        return await super().execute(converted_query, asyncpg_args, timeout=timeout)

    async def fetchx(self, query: str, args: typing.Dict, timeout: typing.Optional[float] = None):
        """Extended versions of `fetch` with support of the named
        parameters."""
        converted_query, asyncpg_args = self._prepare_asyncpg_parameters(
            query, args, query_module.QueryParamsDictConverter()
        )
        return await super().fetch(converted_query, *asyncpg_args, timeout=timeout)

    async def fetchvalx(self, query: str, args: typing.Dict, column: int = 0, timeout: typing.Optional[float] = None):
        """Extended versions of `fetchval` with support of the named
        parameters."""
        converted_query, asyncpg_args = self._prepare_asyncpg_parameters(
            query, args, query_module.QueryParamsDictConverter()
        )
        return await super().fetchval(converted_query, *asyncpg_args, column=column, timeout=timeout)

    async def fetchrowx(self, query: str, args: typing.Dict, timeout: typing.Optional[float] = None):
        """Extended versions of `fetchrow` with support of the named
        parameters."""
        converted_query, asyncpg_args = self._prepare_asyncpg_parameters(
            query, args, query_module.QueryParamsDictConverter()
        )
        return await super().fetchrow(converted_query, *asyncpg_args, timeout=timeout)
