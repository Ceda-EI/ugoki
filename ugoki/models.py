from sqlalchemy import Boolean, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from . import config
from .database import Base


class Category(Base):
    __tablename__ = "categories"

    name = Column(String, primary_key=True)
    gifs = relationship("Gif", back_populates="category")

    def __repr__(self):
        return f"<Category name={self.name!r}>"


class Gif(Base):
    __tablename__ = "gifs"

    id = Column(String, primary_key=True)
    category_name = Column(String, ForeignKey("categories.name"),
                           nullable=False)
    approved = Column(Boolean, nullable=False)

    category = relationship("Category", back_populates="gifs")

    @property
    def url(self):
        return config.SERVE_ROOT + "/" + self.id + ".gif"

    def __repr__(self):
        return f"<Gif id={self.id!r} category_name={self.category_name!r}>"
