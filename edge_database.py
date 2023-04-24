from sqlalchemy import create_engine, String
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

url = URL.create(
        drivername="postgresql+psycopg2",
        username="user",
        password="password",
        host="localhost",
        port=5432,
        database="edge_db"
        )

engine = create_engine(url)

connection = engine.connect()

Base = declarative_base()

class HousePool(Base):
    __tablename__ = 'house_pool'

    id: Mapped[int] = mapped_column(primary_key=True)

if __name__ == "__main__":
    Base.metadata.create_all(engine)
