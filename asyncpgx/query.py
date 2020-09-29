"""Module with tools for queries processing."""
import abc
import re
import typing


class QueryParamsConverter(abc.ABC):
    """Abstract class for converting our high-level API for low-level asyncpg
    API."""

    params_regexp: re.Pattern = re.compile(r"(?<![:\w\x5c]):(\w+)(?!:)", re.UNICODE)

    def construct_asyncpg_query(self, query: str) -> typing.Tuple[str, typing.List]:
        """Construct asyncpg query from high-level one."""
        i: int = 1
        params_order_list: typing.List = []

        def _construct_replacement(match_obj: re.Match) -> str:
            nonlocal i
            new_numeric_param: str = f'${i}'
            params_order_list.append(match_obj.group(0)[1::])
            i += 1
            return new_numeric_param

        query = self.params_regexp.sub(_construct_replacement, query)
        return query, params_order_list

    @abc.abstractmethod
    def prepare_asyncpg_args(self, original_args: typing.Any, params_order_list: typing.List) -> typing.List:
        """Prepare asyncpg method arguments."""
        raise NotImplementedError()  # pragma: no cover


class QueryParamsListDictConverter(QueryParamsConverter):
    """Converts list of dicts named parameters to the asyncpg-friendly
    format."""

    def prepare_asyncpg_args(self, original_args: typing.List[typing.Dict], params_order_list: typing.List):
        """Prepare asyncpg method arguments."""
        asyncpg_args: typing.List = []
        for arg in original_args:
            one_list: typing.List = []
            for param in params_order_list:
                one_list.append(arg[param])
            asyncpg_args.append(one_list)

        return asyncpg_args


class QueryParamsDictConverter(QueryParamsConverter):
    """Converts dict named parameters to the asyncpg-friendly format."""

    def prepare_asyncpg_args(self, original_args: typing.Dict, params_order_list: typing.List):
        """Prepare asyncpg method arguments."""
        asyncpg_args: typing.List = []
        for param in params_order_list:
            asyncpg_args.append(original_args[param])
        return asyncpg_args
