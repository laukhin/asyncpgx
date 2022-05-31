"""Module with tools for queries processing."""
import abc
import re
import typing

from asyncpgx import exceptions


PARAMS_REGEXP = re.compile(r"(?<![:\w\x5c]):(\w+)(?!:)", re.UNICODE)


def construct_asyncpg_query(query: str) -> typing.Tuple[str, typing.List]:
    """Construct asyncpg query from high-level one."""
    i = 1
    params_order_list = []

    def _construct_replacement(match_obj: typing.Match) -> str:
        nonlocal i
        new_numeric_param = f'${i}'
        params_order_list.append(match_obj.group(0)[1::])
        i += 1
        return new_numeric_param

    query = PARAMS_REGEXP.sub(_construct_replacement, query)
    return query, params_order_list


# pylint: disable=too-few-public-methods
class QueryParamsConverter(abc.ABC):
    """Abstract class for converting our high-level API to low-level asyncpg
    API."""

    @abc.abstractmethod
    def prepare_asyncpg_args(self, original_args: typing.Any, params_order_list: typing.List) -> typing.List:
        """Prepare asyncpg method arguments."""
        raise NotImplementedError()  # pragma: no cover


class QueryParamsListDictConverter(QueryParamsConverter):
    """Converts list of dicts named parameters to the asyncpg-friendly
    format."""

    def prepare_asyncpg_args(
        self, original_args: typing.List[typing.Dict], params_order_list: typing.List
    ) -> typing.List:
        """Prepare asyncpg method arguments."""
        asyncpg_args = []
        for arg in original_args:
            asyncpg_args.append(QueryParamsDictConverter().prepare_asyncpg_args(arg, params_order_list))

        return asyncpg_args


class QueryParamsDictConverter(QueryParamsConverter):
    """Converts dict named parameters to the asyncpg-friendly format."""

    def prepare_asyncpg_args(self, original_args: typing.Dict, params_order_list: typing.List) -> typing.List:
        """Prepare asyncpg method arguments."""
        asyncpg_args = []
        used_arguments = set()
        for param in params_order_list:
            try:
                asyncpg_args.append(original_args[param])
            except KeyError as exc:
                raise exceptions.MissingRequiredArgumentError(f'Missing required argument: {param}') from exc

            used_arguments.add(param)

        if len(used_arguments) != len(original_args):
            unused_arguments = set(original_args.keys()).difference(used_arguments)
            raise exceptions.UnusedArgumentsError(f'Arguments: {unused_arguments} are unused')

        return asyncpg_args
