from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from study.database.models_ar import Base
from study.database.models_ar import Color, Tag, Vendor, Volume, Transmission, Bodytype, Fuel, Power
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

    colors = []
    transmissions = []
    vendors = []
    body_types = []
    fuels = []
    engine_volumes = []
    powers = []
    tags = []


    def addtolist(old_list, new_value_path):
        if new_value_path not in old_list:
            old_list.append(new_value_path)


    for offer in offers:
        addtolist(colors, offer['color_hex'])
        addtolist(body_types, offer['vehicle_info']['configuration']['body_type'])
        addtolist(vendors, offer['vehicle_info']['vendor'])
        addtolist(transmissions, offer['vehicle_info']['tech_param']['transmission'])
        addtolist(fuels, offer['vehicle_info']['tech_param']['engine_type'])
        addtolist(powers, offer['vehicle_info']['tech_param']['power'])

        new_volume = offer['vehicle_info']['tech_param']['displacement']
        new_volume = round(new_volume / 1000, 1)
        if new_volume not in engine_volumes:
            engine_volumes.append(new_volume)

        for tag in offer['tags']:
            if tag not in tags:
                tags.append(tag)

    db_colors = [Color(itm, itm) for itm in colors]
    db_tags = [Tag(itm) for itm in tags]
    db_trsmns = [Transmission(itm) for itm in transmissions]
    db_vendors = [Vendor(itm) for itm in vendors]
    db_bodies = [Bodytype(itm) for itm in body_types]
    db_fuels = [Fuel(itm) for itm in fuels]
    db_volumes = [Volume(itm) for itm in engine_volumes]
    db_powers = [Power(itm) for itm in powers]
    db.session.add_all(db_colors)
    db.session.add_all(db_tags)
    db.session.add_all(db_trsmns)
    db.session.add_all(db_vendors)
    db.session.add_all(db_bodies)
    db.session.add_all(db_fuels)
    db.session.add_all(db_volumes)
    db.session.add_all(db_powers)
    db.session.commit()

