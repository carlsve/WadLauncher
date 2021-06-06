from dataclasses import dataclass, field
from core.base.Schema import _SchemaBase, _SchemaDefaultsBase

@dataclass
class _CategoryBase(_SchemaBase):
    pass

@dataclass
class _CategoryDefaultsBase(_SchemaDefaultsBase):
    name: str = 'New Category'
    is_root: bool = False
    children: list = field(default_factory=lambda: [])

@dataclass
class Category(_CategoryDefaultsBase, _CategoryBase):
    @property
    def display_name(self):
        return self.name
