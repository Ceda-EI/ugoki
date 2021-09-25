"Database Models"
from sqlalchemy import Boolean, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from . import config
from .database import Base


class Category(Base):
    "Category"
    __tablename__ = "categories"

    name = Column(String, primary_key=True)
    gifs = relationship("Gif", back_populates="category")

    def __repr__(self):
        return f"<Category name={self.name!r}>"

    @property
    def count(self):
        "Number of approved gifs in this category"
        return len([gif for gif in self.gifs if gif.approved])


class Gif(Base):
    "Gif or Suggestion - If approved, it is a gif. If not, it is a suggestion."
    __tablename__ = "gifs"

    id = Column(String, primary_key=True)
    category_name = Column(String, ForeignKey("categories.name"),
                           nullable=False)
    approved = Column(Boolean, nullable=False)

    category = relationship("Category", back_populates="gifs")

    @property
    def url(self):
        "Returns URL where it is served"
        return config.SERVE_ROOT + "/" + self.id + ".gif"

    def __repr__(self):
        return f"<Gif id={self.id!r} category_name={self.category_name!r}>"
