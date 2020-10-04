"""Module with extensions of asyncpg `PreparedStatement` class."""
import typing

import asyncpg.prepared_stmt
import asyncpg.protocol

from asyncpgx import query as query_module


class PreparedStatementX(asyncpg.prepared_stmt.PreparedStatement):
    """Extended version of asyncpg `PreparedStatement` class.

    Provides various extension methods, but doesn't touches the original
    ones
    """

    __slots__ = ('_original_query', '_params_order_list')

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        connection: asyncpg.Connection,
        query: str,
        state,
        original_query: str,
        params_order_list: typing.List,
    ):
        super().__init__(connection, query, state)
        self._original_query = original_query
        self._params_order_list = params_order_list

    def named_cursor(
        self,
        args: typing.Dict,
        prefetch: typing.Optional[int] = None,
        timeout: typing.Optional[float] = None,
    ):
        """Extended version of `cursor` with support of the named
        parameters."""
        prepared_args = query_module.QueryParamsDictConverter().prepare_asyncpg_args(args, self._params_order_list)
        return super().cursor(*prepared_args, prefetch=prefetch, timeout=timeout)

    async def named_fetch(self, args: typing.Dict, timeout: typing.Optional[float] = None):
        """Extended version of `fetch` with support of the named parameters."""
        prepared_args = query_module.QueryParamsDictConverter().prepare_asyncpg_args(args, self._params_order_list)
        return await super().fetch(*prepared_args, timeout=timeout)

    async def named_fetchval(self, args: typing.Dict, column: int = 0, timeout: typing.Optional[float] = None):
        """Extended version of `fetchval` with support of the named
        parameters."""
        prepared_args = query_module.QueryParamsDictConverter().prepare_asyncpg_args(args, self._params_order_list)
        return await super().fetchval(*prepared_args, column=column, timeout=timeout)

    async def named_fetchrow(self, args: typing.Dict, timeout: typing.Optional[float] = None):
        """Extended version of `fetchrow` with support of the named
        parameters."""
        prepared_args = query_module.QueryParamsDictConverter().prepare_asyncpg_args(args, self._params_order_list)
        return await super().fetchrow(*prepared_args, timeout=timeout)
