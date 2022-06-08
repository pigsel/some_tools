from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from study.database.models_ar import (Base)


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
    print(1)

    #TODO create dicts of colors, tags, fuels, volumes, powers, bodytypes, vendors, transmissions