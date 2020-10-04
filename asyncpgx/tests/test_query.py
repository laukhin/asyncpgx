"""Tests for `query` module."""
from asyncpgx import query


def test_construct_query():
    """Test converter construct query."""
    new_query, params_order_list = query.construct_asyncpg_query(
        '''SELECT * FROM some_table WHERE id=:id AND some_field_1=:some_field_1 AND some_field_2=:some_field_2;'''
    )

    expected_new_query = '''SELECT * FROM some_table WHERE id=$1 AND some_field_1=$2 AND some_field_2=$3;'''
    assert new_query == expected_new_query
    assert params_order_list == ['id', 'some_field_1', 'some_field_2']


def test_list_dict_converter_prepare_asyncpg_args():
    """Test `prepare_asyncpg_args` for list dict converter."""
    converter = query.QueryParamsListDictConverter()

    asyncpg_args = converter.prepare_asyncpg_args(
        [
            {'some_field_1': '1', 'some_field_2': '2', 'some_field_3': '3'},
            {'some_field_1': '4', 'some_field_2': '5', 'some_field_3': '6'},
            {'some_field_1': '7', 'some_field_2': '8', 'some_field_3': '9'},
        ],
        ['some_field_1', 'some_field_2', 'some_field_3'],
    )

    assert asyncpg_args == [['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9']]


def test_dict_converter_prepare_asyncpg_args():
    """Test `prepare_asyncpg_args` for dict converter."""
    converter = query.QueryParamsDictConverter()

    asyncpg_args = converter.prepare_asyncpg_args(
        {'some_field_1': '1', 'some_field_2': '2', 'some_field_3': '3'},
        ['some_field_1', 'some_field_2', 'some_field_3'],
    )

    assert asyncpg_args == ['1', '2', '3']
