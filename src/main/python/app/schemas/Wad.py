import uuid

from dataclasses import dataclass
from core.base.Schema import _SchemaBase, _SchemaDefaultsBase

@dataclass
class _WadBase(_SchemaBase):
    name: str
    path: str
    file_paths: list
    file_path: str

@dataclass
class _WadDefaultsBase(_SchemaDefaultsBase):
    id: str = str(uuid.uuid1())
    title: str = None
    dir: str = None
    filename: str = None
    size: int = None
    age: int = None
    date: str = None
    author: str = None
    email: str = None
    description: str = None
    credits: str = None
    base: str = None
    buildtime: str = None
    editors: str = None
    bugs: str = None
    textfile: str = None
    rating: float = None
    votes: int = 0
    url: str = None
    idgamesurl: str = None
    reviews: object = None
    meta: object = None
    error: object = None

@dataclass
class Wad(_WadDefaultsBase, _WadBase):
    def display_name(self):
        return self.title or self.name
