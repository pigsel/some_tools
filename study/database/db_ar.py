from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from study.database.models_ar import Base
from study.database.models_ar import \
    Color, \
    Tag, \
    Vendor, \
    Volume, \
    Transmission, \
    Bodytype, \
    Fuel, \
    Power, \
    Wheeldrive, \
    Owner, \
    Engine, \
    Car, \
    Offer

import json


class AutoruDb:
    def __init__(self, db_url, base=Base):
        engine = create_engine(db_url)
        base.metadata.create_all(engine)
        session_db = sessionmaker(bind=engine)
        self.__session = session_db()

    @property
    def session(self):
        return self.__session


if __name__ == '__main__':
    db_url = 'sqlite:///aru.sqlite'
    db = AutoruDb(db_url)

    with open("../autoru.json", "r") as read_file:
        offers = json.load(read_file)


    # проход 1 - наполнение независимых таблиц
    colors = []
    transmissions = []
    vendors = []
    body_types = []
    fuels = []
    engine_volumes = []
    powers = []
    tags = []
    owners = []
    wdtypes = []


    def addtolist(old_list, new_value_path):
        if new_value_path not in old_list:
            old_list.append(new_value_path)


    def engineprop():
        power = offer['vehicle_info']['tech_param']['power']
        power_id = db.session.query(Power).filter_by(horsepower=power).first()
        volume = offer['vehicle_info']['tech_param']['displacement']
        volume_id = db.session.query(Volume).filter_by(engine_volume=round(volume / 1000, 1)).first()
        fuel = offer['vehicle_info']['tech_param']['engine_type']
        fuel_id = db.session.query(Fuel).filter_by(name=fuel).first()

        return power_id, volume_id, fuel_id


    for offer in offers:
        addtolist(owners, [offer['seller_type'] == 'PRIVATE', offer['seller']['name']])
        addtolist(colors, offer['color_hex'])
        addtolist(body_types, offer['vehicle_info']['configuration']['body_type'])
        addtolist(vendors, offer['vehicle_info']['vendor'])
        addtolist(transmissions, offer['vehicle_info']['tech_param']['transmission'])
        addtolist(fuels, offer['vehicle_info']['tech_param']['engine_type'])
        addtolist(powers, offer['vehicle_info']['tech_param']['power'])
        addtolist(wdtypes, offer['vehicle_info']['tech_param']['gear_type'])

        new_volume = offer['vehicle_info']['tech_param']['displacement']
        new_volume = round(new_volume / 1000, 1)
        if new_volume not in engine_volumes:
            engine_volumes.append(new_volume)

        for tag in offer['tags']:
            if tag not in tags:
                tags.append(tag)

    db_owners = [Owner(itm[1], itm[0]) for itm in owners]
    db_colors = [Color(itm, itm) for itm in colors]
    db_tags = [Tag(itm) for itm in tags]
    db_trsmns = [Transmission(itm) for itm in transmissions]
    db_vendors = [Vendor(itm) for itm in vendors]
    db_bodies = [Bodytype(itm) for itm in body_types]
    db_fuels = [Fuel(itm) for itm in fuels]
    db_volumes = [Volume(itm) for itm in engine_volumes]
    db_powers = [Power(itm) for itm in powers]
    db_wdtypes = [Wheeldrive(itm) for itm in wdtypes]
    db.session.add_all(db_owners)
    db.session.add_all(db_colors)
    db.session.add_all(db_tags)
    db.session.add_all(db_trsmns)
    db.session.add_all(db_vendors)
    db.session.add_all(db_bodies)
    db.session.add_all(db_fuels)
    db.session.add_all(db_volumes)
    db.session.add_all(db_powers)
    db.session.add_all(db_wdtypes)
    db.session.commit()

    # проход 2 - наполнение таблицы двигателей с зависимостями
    engines = []

    for offer in offers:
        power_id, volume_id, fuel_id = engineprop()
        addtolist(engines, [power_id, volume_id, fuel_id])

    db_engines = [Engine(itm[0], itm[1], itm[2]) for itm in engines]
    db.session.add_all(db_engines)
    db.session.commit()


    # проход 3 - наполнение таблицы моделей машин
    cars = []

    for offer in offers:
        # brand: str, model: str, engine, bodytype, doors: int,
        # fullwd, rightwheel: bool, transmission, vendor

        brand = offer['vehicle_info']['mark_info']['name']
        model = offer['vehicle_info']['model_info']['name']

        # engine
        power_id, volume_id, fuel_id = engineprop()
        engine = db.session.query(Engine).\
            filter_by(power=power_id). \
            filter_by(volume=volume_id). \
            filter_by(fuel=fuel_id).\
            first()

        bodytype = offer['vehicle_info']['configuration']['body_type']
        bodytype_id = db.session.query(Bodytype).filter_by(name=bodytype).first()
        doors = offer['vehicle_info']['configuration']['doors_count']
        wdtype = offer['vehicle_info']['tech_param']['gear_type']
        wdtype_id = db.session.query(Wheeldrive).filter_by(name=wdtype).first()
        rightwheel = offer['vehicle_info']['steering_wheel']  # == ?
        transmission = offer['vehicle_info']['tech_param']['transmission']
        transmission_id = db.session.query(Transmission).filter_by(name=transmission).first()
        vendor = offer['vehicle_info']['vendor']
        vendor_id = db.session.query(Vendor).filter_by(name=vendor).first()

        addtolist(cars, [brand, model, engine, bodytype_id, doors,
                         wdtype_id, rightwheel == 'RIGHT', transmission_id, vendor_id])

    db_cars = [Car(itm[0], itm[1], itm[2], itm[3], itm[4], itm[5], itm[6], itm[7], itm[8]) for itm in cars]
    db.session.add_all(db_cars)
    db.session.commit()


    # проход 4 - финальный проход - заполнение оферов
    newoffers = []
    # car_id, creation_date: int, price: int, color, owner,
    # yearold: int, mileage: int, beaten: bool, tags = []

    for offer in offers:
        # choose car
        brand = offer['vehicle_info']['mark_info']['name']
        model = offer['vehicle_info']['model_info']['name']

        power_id, volume_id, fuel_id = engineprop()
        engine = db.session.query(Engine).\
            filter_by(power=power_id). \
            filter_by(volume=volume_id). \
            filter_by(fuel=fuel_id).\
            first()

        bodytype = offer['vehicle_info']['configuration']['body_type']
        bodytype_id = db.session.query(Bodytype).filter_by(name=bodytype).first()
        doors = offer['vehicle_info']['configuration']['doors_count']
        wdtype = offer['vehicle_info']['tech_param']['gear_type']
        wdtype_id = db.session.query(Wheeldrive).filter_by(name=wdtype).first()
        rightwheel = (offer['vehicle_info']['steering_wheel'] == 'RIGHT')
        transmission = offer['vehicle_info']['tech_param']['transmission']
        transmission_id = db.session.query(Transmission).filter_by(name=transmission).first()
        vendor = offer['vehicle_info']['vendor']
        vendor_id = db.session.query(Vendor).filter_by(name=vendor).first()

        car = db.session.query(Car). \
            filter_by(brand=brand). \
            filter_by(model=model). \
            filter_by(engine=engine). \
            filter_by(bodytype=bodytype_id). \
            filter_by(doors=doors). \
            filter_by(wdtype=wdtype_id). \
            filter_by(rightwheel=rightwheel). \
            filter_by(transmission=transmission_id). \
            filter_by(vendor=vendor_id). \
            first()

        creation_date = offer['additional_info']['creation_date']
        price = offer['price_info']['USD']
        color = offer['color_hex']
        color_id = db.session.query(Color).filter_by(name=color).first()
        owner = offer['seller']['name']
        owner_id = db.session.query(Owner).filter_by(name=owner).first()
        yearold = offer['documents']['year']
        mileage = offer['state']['mileage']
        beaten = offer['state']['state_not_beaten']
        tagsdb = []
        for newtag in offer['tags']:
            tagsdb.append(db.session.query(Tag).filter_by(name=newtag).first())

        addtolist(newoffers, [car, creation_date, price, color_id, owner_id,
                              yearold, mileage, beaten, tagsdb])

        #print(1)

    db_offers = [Offer(itm[0], itm[1], itm[2], itm[3], itm[4], itm[5], itm[6], itm[7], itm[8]) for itm in newoffers]
    db.session.add_all(db_offers)
    db.session.commit()
