"Pydantic schemas"
# pylint: disable=R0903,E0611
from pydantic import BaseModel


class Category(BaseModel):
    "Category returned in /categories"
    name: str
    count: int

    class Config:
        "Pydantic Config"
        orm_mode = True


class Gif(BaseModel):
    "Gif returned in /category/{name}/gif"
    id: str
    url: str

    class Config:
        orm_mode = True


class Suggestion(Gif):
    "Suggestion"
    category_name: str


class Success(BaseModel):
    "Success"
    success: bool
