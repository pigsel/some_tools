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
    Column('offer', Integer, ForeignKey('offer.id')),
    Column('tag', Integer, ForeignKey('tag.id')),
)


# класс записи в блоге
class Offer(Base):
    __tablename__ = 'offer'
    id = Column(Integer, primary_key=True, autoincrement=True)
    #creation_date
    price = Column(Integer)
    url = Column(String, unique=True)
    color_hex = Column(String, ForeignKey('color.hex'))
    color = relationship('Color', backref='offers')
    __owner = Column(Integer, ForeignKey('owner.id'))
    owner = relationship('Owner', backref='offers')
    #year = Column(Integer)
    #mileage
    tags = relationship('Tag', secondary=assoc_offer_tag, backref='offers')

    def __init__(self, price: int, url: str, color, owner, tags=[]):
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
    isprivate = Column(Boolean)

    def __init__(self, name: str, url: str, isprivate: bool):
        self.name = name
        self.url = url
        self.isprivate = isprivate


# класс colors
class Color(Base):
    __tablename__ = 'color'
    hex = Column(String, primary_key=True, unique=True)
    name = Column(String, unique=True)

    def __init__(self, hex: str, name: str):
        self.hex = hex
        self.name = name


class Engine(Base):
    __tablename__ = 'engine'
    id = Column(Integer, primary_key=True, autoincrement=True)
    power = Column(Integer, unique=True)
    volume = Column(Integer, unique=True)
    fuel = Column(String, unique=True)

    def __init__(self, power: int, volume: int, fuel: str):
        self.power = power
        self.volume = volume
        self.fuel = fuel


class Car(Base):
    __tablename__ = 'cars'
    id = Column(Integer, primary_key=True, autoincrement=True)
    brand = Column(String)
    model = Column(String)
    bodytype = Column(String)
    doors = Column(Integer)
    fullwd = Column(Boolean)
    rightwheel = Column(Boolean)
    transmission = Column(String)
    vendor = Column(String)

    def __init__(self, brand: str, model: str, bodytype: str, doors: int,
                 fullwd: bool, rightwheel: bool, transmission: str, vendor: str):
        self.brand = brand
        self.model = model
        self.bodytype = bodytype
        self.doors = doors
        self.fullwd = fullwd
        self.rightwheel = rightwheel
        self.transmission = transmission
        self.vendor = vendor


#TODO add table bodytype
#TODO add table transmission
#TODO add table bvendor
#TODO add table power
#TODO add table volume
#TODO add table fuel

