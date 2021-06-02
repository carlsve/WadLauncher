import uuid

from dataclasses import dataclass

@dataclass
class _SchemaBase:
    model_type: str

@dataclass
class _SchemaDefaultsBase:
    id: str = str(uuid.uuid1())

@dataclass
class Schema(_SchemaDefaultsBase, _SchemaBase):
    pass
