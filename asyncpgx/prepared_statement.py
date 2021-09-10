"""Module with extensions of asyncpg `PreparedStatement` class."""
import typing

import asyncpg
import asyncpg.cursor
import asyncpg.prepared_stmt

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
        state: typing.Any,  # i couldn't import PreparedStatementState
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
    ) -> asyncpg.cursor.CursorFactory:
        """Extended version of `cursor` with support of the named parameters.

        :param args: Dict with the parameters values.
        :param prefetch: The number of rows the *cursor iterator* will prefetch (defaults to ``50``.)
        :param timeout: Optional timeout value in seconds.
        """
        prepared_args = query_module.QueryParamsDictConverter().prepare_asyncpg_args(args, self._params_order_list)
        return super().cursor(*prepared_args, prefetch=prefetch, timeout=timeout)

    async def named_fetch(
        self, args: typing.Dict, timeout: typing.Optional[float] = None
    ) -> typing.List[asyncpg.Record]:
        """Extended version of `fetch` with support of the named parameters.

        :param args: Dict with the parameters values.
        :param timeout: Optional timeout value in seconds.
        """
        prepared_args = query_module.QueryParamsDictConverter().prepare_asyncpg_args(args, self._params_order_list)
        query_result: typing.List[asyncpg.Record] = await super().fetch(*prepared_args, timeout=timeout)
        return query_result

    async def named_fetchval(
        self, args: typing.Dict, column: int = 0, timeout: typing.Optional[float] = None
    ) -> typing.Any:
        """Extended version of `fetchval` with support of the named parameters.

        :param args: Dict with the parameters values.
        :param column: Numeric index within the record of the value to return.
        :param timeout: Optional timeout value in seconds.
        """
        prepared_args = query_module.QueryParamsDictConverter().prepare_asyncpg_args(args, self._params_order_list)
        return await super().fetchval(*prepared_args, column=column, timeout=timeout)

    async def named_fetchrow(self, args: typing.Dict, timeout: typing.Optional[float] = None) -> asyncpg.Record:
        """Extended version of `fetchrow` with support of the named parameters.

        :param args: Dict with the parameters values.
        :param timeout: Optional timeout value in seconds.
        """
        prepared_args = query_module.QueryParamsDictConverter().prepare_asyncpg_args(args, self._params_order_list)
        return await super().fetchrow(*prepared_args, timeout=timeout)
