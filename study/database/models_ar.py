from sqlalchemy import (
    Table,
    Column,
    ForeignKey,
    String,
    Integer,
    Boolean,
)

from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

assoc_offer_tag = Table(
    'offer_tag',
    Base.metadata,
    Column('offer', Integer, ForeignKey('blogpost.id')),
    Column('tag', Integer, ForeignKey('tag.id')),
)


# класс записи в блоге
class Offer(Base):
    __tablename__ = 'offers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    price = Column(Integer)
    url = Column(String, unique=True)
    color_id = Column(Integer, ForeignKey('color.id'))
    color = relationship('Color', backref='offers')
    owner_id = Column(Integer, ForeignKey('owner.id'))
    owner = relationship('Owner', backref='offers')
    tags = relationship('Tag', secondary=assoc_offer_tag, backref='offers')

    def __init__(self, price: int, url: str, color, owner, tags=tuple()):
        self.price = price
        self.url = url
        self.color = color
        self.owner = owner
        if tags:
            self.tags.extend(tags)


# класс для объекта тега
class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)

    def __init__(self, name: str):
        self.name = name


# класс автора блога
class Owner(Base):
    __tablename__ = 'owner'
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, unique=True)
    name = Column(String)

    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url


# класс colors
class Color(Base):
    __tablename__ = 'color'
    hex = Column(String, primary_key=True, unique=True)
    name = Column(String, unique=True)

    def __init__(self, hex: str, name: str):
        self.hex = hex
        self.name = name


class Car(Base):
    __tablename__ = 'cars'
    id = Column(Integer, primary_key=True, autoincrement=True)
    brand = Column(String)
    model = Column(String)
    type = Column(String)
    power = Column(String)
    fuel = Column(String)
    doors = Column(String)
    fullwd = Column(Boolean)
    rightwheel = Column(Boolean)
    transmission = Column(String)


    def __init__(self, name: str):
        self.name = name
