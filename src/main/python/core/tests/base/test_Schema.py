from unittest import TestCase
from dataclasses import dataclass, asdict

from core.base.Schema import _SchemaBase, _SchemaDefaultsBase

case = TestCase()

# ----- MOCK DATA -----
@dataclass
class _MockSchemaBase(_SchemaBase):
    required: str

@dataclass
class _MockSchemaDefaultsBase(_SchemaDefaultsBase):
    name: str = "New Mock"
    is_test: bool = None

@dataclass
class MockSchema(_MockSchemaDefaultsBase, _MockSchemaBase):
    pass

mock_params = {
    'name': 'testname',
    'id': 'testid',
    'required': 'test_val',
    'model_type': 'test_model',
    'is_test': True
}


# ----- TEST CASES -----
def test_instance_creation():
    with case.assertRaises(TypeError):
        mock_data = MockSchema()

    mock_data = MockSchema(required='test_val', model_type='test_model')
    assert mock_data.id != None
    assert mock_data.name == "New Mock"
    assert mock_data.is_test == None

def test_parameter_instantiation():
    mock_data = MockSchema(**mock_params)

    assert mock_data.id == mock_params['id']
    assert mock_data.name == mock_params['name']
    assert all([key in mock_params for key in asdict(mock_data)])

