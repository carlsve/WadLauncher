from dataclasses import dataclass
from core.base.Schema import _SchemaBase, _SchemaDefaultsBase

@dataclass
class _IwadBase(_SchemaBase):
    name: str
    path: str

@dataclass
class _IwadDefaultsBase(_SchemaDefaultsBase):
    pass

@dataclass
class Iwad(_IwadDefaultsBase, _IwadBase):
    pass
