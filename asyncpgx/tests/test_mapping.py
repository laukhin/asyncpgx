"""Test for `mapping` module."""
import sys
from collections import namedtuple

import pytest
from pydantic import BaseModel

from asyncpgx import connection as connection_module
from asyncpgx import mapping


OBJECTS_FOR_MAP = []


# pylint: disable=too-few-public-methods
class ObjectForMap:
    """Test object for mapping."""

    # pylint: disable=redefined-builtin
    def __init__(self, id, test_1, test_2):
        self.id = id  # pylint: disable=invalid-name
        self.test_1 = test_1
        self.test_2 = test_2


OBJECTS_FOR_MAP.append(ObjectForMap)

if sys.version_info >= (3, 7):
    import dataclasses

    @dataclasses.dataclass(frozen=True)
    class DataclassForMap:
        """Test dataclass for mapping."""

        id: int  # pylint: disable=invalid-name
        test_1: str
        test_2: str

    OBJECTS_FOR_MAP.append(DataclassForMap)  # type: ignore


class PydanticModelForMap(BaseModel):
    """Test pydantic model for mapping."""

    id: int
    test_1: str
    test_2: str


OBJECTS_FOR_MAP.append(PydanticModelForMap)  # type: ignore

NamedTupleModelForMap = namedtuple('NamedTupleModelForMap', ('id', 'test_1', 'test_2'))
OBJECTS_FOR_MAP.append(NamedTupleModelForMap)  # type: ignore


@pytest.mark.asyncio
async def test_dict_mapper_on_one_record(postgres_connection: connection_module.ConnectionX):
    """Test dict mapper on one record."""
    await postgres_connection.named_execute(
        'INSERT INTO test(id, test_1, test_2) VALUES (:id, :test_1, :test_2);', {'id': 1, 'test_1': '1', 'test_2': '2'}
    )

    record = await postgres_connection.fetchrow('SELECT id, test_1, test_2 FROM test;')

    mapped_dict = mapping.DictDataMapper().map_one(record)
    assert mapped_dict['id'] == 1
    assert mapped_dict['test_1'] == '1'
    assert mapped_dict['test_2'] == '2'


@pytest.mark.asyncio
async def test_dict_mapper_on_multiple_records(postgres_connection: connection_module.ConnectionX):
    """Test dict mapper on multiple records."""
    await postgres_connection.named_executemany(
        '''INSERT INTO test(id, test_1, test_2) VALUES (:id, :test_1, :test_2);''',
        [
            {'id': 1, 'test_1': '1', 'test_2': '1'},
            {'id': 2, 'test_1': '2', 'test_2': '2'},
            {'id': 3, 'test_1': '3', 'test_2': '3'},
        ],
    )

    records = await postgres_connection.fetch('SELECT id, test_1, test_2 FROM test;')

    mapped_list = mapping.DictDataMapper().map_many(records)
    assert mapped_list[0]['id'] == 1
    assert mapped_list[0]['test_1'] == '1'
    assert mapped_list[0]['test_2'] == '1'
    assert mapped_list[1]['id'] == 2
    assert mapped_list[1]['test_1'] == '2'
    assert mapped_list[1]['test_2'] == '2'
    assert mapped_list[2]['id'] == 3
    assert mapped_list[2]['test_1'] == '3'
    assert mapped_list[2]['test_2'] == '3'


@pytest.mark.asyncio
@pytest.mark.parametrize('object_for_map', OBJECTS_FOR_MAP)
async def test_object_mapper_on_one_record(postgres_connection: connection_module.ConnectionX, object_for_map):
    """Test object mapper on one record."""
    await postgres_connection.named_execute(
        'INSERT INTO test(id, test_1, test_2) VALUES (:id, :test_1, :test_2);', {'id': 1, 'test_1': '1', 'test_2': '2'}
    )

    record = await postgres_connection.fetchrow('SELECT id, test_1, test_2 FROM test;')

    mapped_object = mapping.ObjectDataMapper(object_for_map).map_one(record)
    assert mapped_object.id == 1
    assert mapped_object.test_1 == '1'
    assert mapped_object.test_2 == '2'


@pytest.mark.asyncio
@pytest.mark.parametrize('object_for_map', OBJECTS_FOR_MAP)
async def test_object_mapper_on_many_records(postgres_connection: connection_module.ConnectionX, object_for_map):
    """Test object mapper on many records."""
    await postgres_connection.named_executemany(
        '''INSERT INTO test(id, test_1, test_2) VALUES (:id, :test_1, :test_2);''',
        [
            {'id': 1, 'test_1': '1', 'test_2': '1'},
            {'id': 2, 'test_1': '2', 'test_2': '2'},
            {'id': 3, 'test_1': '3', 'test_2': '3'},
        ],
    )

    records = await postgres_connection.fetch('SELECT id, test_1, test_2 FROM test;')

    mapped_list = mapping.ObjectDataMapper(object_for_map).map_many(records)
    assert mapped_list[0].id == 1
    assert mapped_list[0].test_1 == '1'
    assert mapped_list[0].test_2 == '1'
    assert mapped_list[1].id == 2
    assert mapped_list[1].test_1 == '2'
    assert mapped_list[1].test_2 == '2'
    assert mapped_list[2].id == 3
    assert mapped_list[2].test_1 == '3'
    assert mapped_list[2].test_2 == '3'


@pytest.mark.asyncio
@pytest.mark.parametrize('object_for_map', OBJECTS_FOR_MAP)
async def test_object_mapper_fail(postgres_connection: connection_module.ConnectionX, object_for_map):
    """Test object mapper fail."""

    await postgres_connection.named_execute(
        'INSERT INTO test(id, test_1, test_2) VALUES (:id, :test_1, :test_2);', {'id': 1, 'test_1': '1', 'test_2': '2'}
    )

    record = await postgres_connection.fetchrow('SELECT id, test_1 FROM test;')

    with pytest.raises(mapping.MappingError):
        mapping.ObjectDataMapper(object_for_map).map_one(record)
