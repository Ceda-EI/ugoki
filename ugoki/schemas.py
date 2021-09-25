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
