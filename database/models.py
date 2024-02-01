from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

__all__ = ['Website', 'Category', 'Base']

Base = declarative_base()


class Website(Base):
    """Table for sources of data"""
    __tablename__ = 'websites'
    id = Column('id', Integer, primary_key=True, autoincrement=True, index=True)
    title = Column('title', String)
    url = Column('url', String)
    icon = Column('icon', String, default=None)

    category_id = Column('category_id', Integer, ForeignKey('categories.id'), default=1)
    category = relationship('Category', backref='websites')

    def __str__(self):
        return f'{self.title = }, {self.icon = }, {self.category.title}'

    def __repr__(self):
        return f'{self.title = }, {self.icon = }, {self.category.title}'


class Category(Base):
    """Table for categories of data"""
    __tablename__ = 'categories'
    id = Column('id', Integer, primary_key=True, autoincrement=True, index=True)
    title = Column('title', String, unique=True, nullable=False)

    def __str__(self):
        return self.title

    def __repr__(self):
        return self.title
