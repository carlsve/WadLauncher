import json

from unittest import mock, TestCase
from dataclasses import asdict, dataclass

from core.base.Model import Model
from core.base.Schema import _SchemaBase, _SchemaDefaultsBase

case = TestCase()

# ----- MOCK DATA -----
@dataclass
class _MockSchemaBase(_SchemaBase):
    file: str

@dataclass
class _MockSchemaDefaultsBase(_SchemaDefaultsBase):
    name: str = 'New Mock'
    title: str = 'Test Title'
    description: str = 'Test Description'

@dataclass
class MockSchema(_MockSchemaDefaultsBase, _MockSchemaBase):
    pass

mock_data = {
    '0': {'id': '0', 'name': 'going down', 'file': 'gd.wad' },
    '1': {'id': '1', 'name': 'miasma', 'file': 'miasma.wad' },
    '2': {'id': '2', 'name': 'sunder', 'file': 'sunder.wad' },
    '3': {'id': '3', 'file': 'tester.wad', 'model_type': 'something' },
}

def mock_loader():
    return mock_data.values()

def mock_saver(data):
    return json.dumps(data)

# ----- TEST CASES -----
def test_instance_creation():
    mock_model = Model(schema=MockSchema)

def test_loader():
    mock_model = Model(schema=MockSchema, loader=mock_loader)
    mock_model.load()

    for item in mock_model.all():
        assert all([key in asdict(item) for key in mock_data[item.id]])

def test_saver():
    mock_model = Model(schema=MockSchema, loader=mock_loader, saver=mock_saver)
    mock_model.load()

    wad = {'name':'foo', 'file':'foo.wad' }
    id = mock_model.create(**wad)
    json_string = mock_model.save(id)

    assert all([key in json.loads(json_string) for key in {'id':id, **wad}])

def test_create():
    mock_model = Model(schema=MockSchema, loader=mock_loader, saver=mock_saver)
    mock_model.load()

    wad = {'name':'foo', 'file':'foo.wad'}
    id = mock_model.create(**wad)
    assert(asdict(mock_model.find(id)).items() >= wad.items())

    wad2 = {'name':'bar', 'file':'bar.wad'}
    wad2metadata = { 'id': '1234', 'title': 'Bar', 'description': 'This is bar.wad!' }
    id2 = mock_model.create(**wad2, **wad2metadata)
    assert all([key in asdict(mock_model.find(id2)) for key in {**wad2, **wad2metadata}])

def test_find():
    mock_model = Model(schema=MockSchema, loader=mock_loader)
    mock_model.load()

    assert all([key in asdict(mock_model.find('0')) for key in mock_data.get('0')])

def test_find_by():
    mock_model = Model(schema=MockSchema, loader=mock_loader)
    mock_model.load()

    # Finding by one attribute
    item = mock_model.find_by(name='going down')
    assert all([key in asdict(item) for key in mock_data.get('0')])

    # Finding by multiple attributes
    item = mock_model.find_by(name='miasma', file='miasma.wad')
    assert all([key in asdict(item) for key in mock_data.get('1')])

    # Returns None if not found
    assert(mock_model.find_by(name='should not be found', file='miasma.wad', random='none') == None)

def test_update():
    mock_model = Model(schema=MockSchema, loader=mock_loader, saver=mock_saver)
    mock_model.load()

    mock_model.update('2', file='sunder2.wad')
    assert(mock_model.find('2').file == 'sunder2.wad')
    # other attributes should be the same
    assert(mock_model.find_by(id='2', name='sunder', file='sunder2.wad') != None)

    # throw error when trying to update item that doesnt exist
    with case.assertRaises(KeyError):
        mock_model.update('4', name='key error should be thrown')


def test_delete():
    mock_model = Model(schema=MockSchema, loader=mock_loader, saver=mock_saver)
    mock_model.load()

    deleted = mock_model.delete('2')
    assert all([key in asdict(deleted) for key in mock_data.get('2')])

    with case.assertRaises(KeyError):
        mock_model.find('2')

def test_subscribe():
    mock_model = Model(schema=MockSchema, loader=mock_loader)
    mock_func1 = mock.MagicMock()
    mock_func2 = mock.MagicMock()

    unsubscribe = mock_model.subscribe(mock_func1)
    mock_model.subscribe(mock_func2)

    mock_model.broadcast('data')
    mock_func1.assert_called_with('data')
    mock_func2.assert_called_with('data')

    # if unsubscribed, mock_func1 should not be called again
    unsubscribe()
    # mock_func2 should still function as usual
    mock_func2.reset_mock()
    mock_model.broadcast('data')
    mock_func1.assert_called_once_with('data')
    mock_func2.assert_called_with('data')

    
