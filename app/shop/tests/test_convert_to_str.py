# -*- coding: utf-8 -*-
import pytest

from shop.utils import convert_to_str


class SimpleObject:
    class_value = 42

    def __init__(self, key):
        self._key = key
        self.myvalue = 31
        self.boolean = True


class ComplexObject(SimpleObject):
    subclass_value = 53

    def __init__(self, key2, key):
        super().__init__(key)
        self._key2 = key2
        self.myothervalue = 20
        self.boolean = False


class VeryComplexObject:

    def __init__(self, key2, key):
        self.cobj = ComplexObject(key2, key)
        self.sobj = SimpleObject(key)


@pytest.fixture
def cases():
    return [
        'a_string',
        '89',
        91,
        14.6,
        True,
        [ 22, False, 56, 'two' ],
        { 'one': 1, 'two': 2, 'three': 3},
        SimpleObject(22),
        ComplexObject(66, 22),
        VeryComplexObject(66, 22)
    ]

@pytest.fixture
def results():
    return [
        'a_string',
        '89',
        91,
        14.6,
        True,
        [ 22, False, 56, 'two' ],
        { 'one': 1, 'two': 2, 'three': 3},
        {'__type__': 'SimpleObject', '_key': 22, 'myvalue': 31, 'boolean': True},
        {'__type__': 'ComplexObject', '_key': 22, '_key2': 66, 'myothervalue': 20, 'myvalue': 31, 'boolean': False},
        {
            '__type__': 'VeryComplexObject',
            'cobj': {'__type__': 'ComplexObject', '_key': 22, '_key2': 66,
                     'boolean': False, 'myothervalue': 20, 'myvalue': 31},
            'sobj': {'__type__': 'SimpleObject', '_key': 22, 'boolean': True, 'myvalue': 31}
         }
    ,
    ]



def test_convert_to_str(cases, results):
    for case, result in zip(cases, results):
        s = convert_to_str(case)
        assert s == result

