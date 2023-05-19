# initdb.py

from sqlalchemy.orm import sessionmaker
from models import Base, HousePool
from utils import engine


if __name__ == "__main__":
    Base.metadata.create_all(engine)

    houses = []
    for i in range(3):
        houses.append(HousePool(name = f"House {i+1}", ip = f"10.10.0.10{i+1}"))

    Session = sessionmaker(bind=engine)
    session = Session()
    session.add_all(houses)
    session.commit()
