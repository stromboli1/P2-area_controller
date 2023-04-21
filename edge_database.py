from sqlalchemy import create_engine, String
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

url = URL.create(
        drivername="postgresql+psycopg2",
        username="p2database",
        password="p2database",
        host="localhost",
        port=5432,
        database="p2database"
        )

engine = create_engine(url)

connection = engine.connect()

Base = declarative_base()

class HousePool(Base):
    __tablename__ = 'house_pool'

    id: Mapped[int] = mapped_column(primary_key=True)

Base.metadata.create_all(engine)
