from dataclasses import dataclass
from core.base.Schema import _SchemaBase, _SchemaDefaultsBase

@dataclass
class _SourcePortBase(_SchemaBase):
    name: str
    dir: str
    executable: str
    iwad_arg: str
    wad_arg: str
    save_arg: str

@dataclass
class _SourcePortDefaultsBase(_SchemaDefaultsBase):
    pass

@dataclass
class SourcePort(_SourcePortDefaultsBase, _SourcePortBase):
    pass
