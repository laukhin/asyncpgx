"""Module with extensions of asyncpg `Connection` class."""
import functools
import typing

import asyncpg

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
        converted_query, params_order_list = converter.construct_asyncpg_query(query)
        return converted_query, converter.prepare_asyncpg_args(args, params_order_list)

    async def named_execute(self, query: str, args: typing.Dict, timeout: typing.Optional[float] = None) -> str:
        """Extended versions of `execute` with support of the named
        parameters."""
        converted_query, asyncpg_args = self._prepare_asyncpg_parameters(
            query, args, query_module.QueryParamsDictConverter()
        )
        return await super().execute(converted_query, *asyncpg_args, timeout=timeout)

    async def named_executemany(self, query: str, args: typing.List, *, timeout: typing.Optional[float] = None):
        """Extended versions of `executemany` with support of the named
        parameters."""
        converted_query, asyncpg_args = self._prepare_asyncpg_parameters(
            query, args, query_module.QueryParamsListDictConverter()
        )

        return await super().executemany(converted_query, asyncpg_args, timeout=timeout)

    async def named_fetch(self, query: str, args: typing.Dict, timeout: typing.Optional[float] = None):
        """Extended versions of `fetch` with support of the named
        parameters."""
        converted_query, asyncpg_args = self._prepare_asyncpg_parameters(
            query, args, query_module.QueryParamsDictConverter()
        )
        return await super().fetch(converted_query, *asyncpg_args, timeout=timeout)

    async def named_fetchval(
        self, query: str, args: typing.Dict, column: int = 0, timeout: typing.Optional[float] = None
    ):
        """Extended versions of `fetchval` with support of the named
        parameters."""
        converted_query, asyncpg_args = self._prepare_asyncpg_parameters(
            query, args, query_module.QueryParamsDictConverter()
        )
        return await super().fetchval(converted_query, *asyncpg_args, column=column, timeout=timeout)

    async def named_fetchrow(self, query: str, args: typing.Dict, timeout: typing.Optional[float] = None):
        """Extended versions of `fetchrow` with support of the named
        parameters."""
        converted_query, asyncpg_args = self._prepare_asyncpg_parameters(
            query, args, query_module.QueryParamsDictConverter()
        )
        return await super().fetchrow(converted_query, *asyncpg_args, timeout=timeout)


create_pool: typing.Callable = functools.partial(asyncpg.create_pool, connection_class=ConnectionX)
connect: typing.Callable = functools.partial(asyncpg.connect, connection_class=ConnectionX)
