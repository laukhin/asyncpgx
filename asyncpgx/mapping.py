"""Module with mapping functionality."""
import abc
import typing

import asyncpg


class MappingError(ValueError):
    """Error occurred on unsuccessful mapping."""


class BaseDataMapper(abc.ABC):
    """Base data mapper class."""

    @abc.abstractmethod
    def map_one(self, record: asyncpg.Record) -> typing.Any:
        """Map one record to specific object."""
        raise NotImplementedError()  # pragma: no cover

    def map_many(self, records: typing.List[asyncpg.Record]) -> typing.List[typing.Any]:
        """Map many records to the lists if specific objects."""
        mapping_result = []
        for record in records:
            mapping_result.append(self.map_one(record))
        return mapping_result


class DictDataMapper(BaseDataMapper):
    """Dict data mapper class."""

    def map_one(self, record: asyncpg.Record) -> typing.Dict:
        """Map one record to dict."""
        mapping_result = {}
        for key, value in record.items():
            mapping_result[key] = value
        return mapping_result


class ObjectDataMapper(BaseDataMapper):
    """Object data mapper class."""

    def __init__(self, object_class: typing.Type):
        self._object_class = object_class

    def map_one(self, record: asyncpg.Record) -> typing.Any:
        """Map one record to `object_class` class instance."""
        try:
            return self._object_class(**record)
        except (TypeError, ValueError) as exc:
            raise MappingError(f'Error on record mapping. Original error text: {exc}') from exc
