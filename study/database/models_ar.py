from sqlalchemy import (
    Table,
    Column,
    ForeignKey,
    String,
    Integer,
    Boolean,
    Float,
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
    car_id = Column(Integer, ForeignKey('car.id'))
    car = relationship('Car', backref='offers')
    creation_date = Column(Integer)
    price = Column(Integer)
    color_hex = Column(String, ForeignKey('color.hex'))
    color = relationship('Color', backref='offers')
    __owner = Column(Integer, ForeignKey('owner.id'))
    owner = relationship('Owner', backref='offers')
    yearold = Column(Integer)
    mileage = Column(Integer)
    beaten = Column(Boolean)    #state_not_beaten
    tags = relationship('Tag', secondary=assoc_offer_tag, backref='offers')

    def __init__(self, creation_date: int, price: int, color, owner,
                 yearold: int, mileage: int, beaten: bool, tags=[]):
        self.creation_date = creation_date
        self.price = price
        self.color = color
        self.owner = owner
        self.yearold = yearold
        self.mileage = mileage
        self.beaten = beaten
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
    name = Column(String)
    isprivate = Column(Boolean)

    def __init__(self, name: str, isprivate: bool):
        self.name = name
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
    power_id = Column(Integer, ForeignKey('power.id'))
    power = relationship('Power', backref='engines')
    volume_id = Column(Integer, ForeignKey('volume.id'))
    volume = relationship('Volume', backref='engines')
    fuel_id = Column(String, ForeignKey('fuel.id'))
    fuel = relationship('Fuel', backref='engines')

    def __init__(self, power, volume, fuel):
        self.power = power
        self.volume = volume
        self.fuel = fuel


class Car(Base):
    __tablename__ = 'car'
    id = Column(Integer, primary_key=True, autoincrement=True)
    brand = Column(String)
    model = Column(String)
    engine_id = Column(Integer, ForeignKey('engine.id'))
    engine = relationship('Engine', backref='cars')
    bodytype_id = Column(Integer, ForeignKey('bodytype.id'))
    bodytype = relationship('Bodytype', backref='cars')
    doors = Column(Integer)
    fullwd = Column(Boolean)
    rightwheel = Column(Boolean)
    transmission_id = Column(Integer, ForeignKey('transmission.id'))
    transmission = relationship('Transmission', backref='cars')
    vendor_id = Column(Integer, ForeignKey('vendor.id'))
    vendor = relationship('Vendor', backref='cars')

    def __init__(self, brand: str, model: str, engine, bodytype, doors: int,
                 fullwd: bool, rightwheel: bool, transmission, vendor):
        self.brand = brand
        self.model = model
        self.engine = engine
        self.bodytype = bodytype
        self.doors = doors
        self.fullwd = fullwd
        self.rightwheel = rightwheel
        self.transmission = transmission
        self.vendor = vendor


#add table bodytype
class Bodytype(Base):
    __tablename__ = 'bodytype'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)

    def __init__(self, name: str):
        self.name = name


#add table transmission
class Transmission(Base):
    __tablename__ = 'transmission'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)

    def __init__(self, name: str):
        self.name = name


#add table vendor
class Vendor(Base):
    __tablename__ = 'vendor'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)

    def __init__(self, name: str):
        self.name = name


#add table power
class Power(Base):
    __tablename__ = 'power'
    id = Column(Integer, primary_key=True, autoincrement=True)
    horsepower = Column(Integer, unique=True)

    def __init__(self, horsepower: int):
        self.horsepower = horsepower


#add table volume
class Volume(Base):
    __tablename__ = 'volume'
    id = Column(Integer, primary_key=True, autoincrement=True)
    engine_volume = Column(Float, unique=True)

    def __init__(self, engine_volume: int):
        self.engine_volume = engine_volume


#add table fuel
class Fuel(Base):
    __tablename__ = 'fuel'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)

    def __init__(self, name: str):
        self.name = name

