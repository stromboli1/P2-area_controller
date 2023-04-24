from sqlalchemy import create_engine, String, ForeignKey, Integer, Float, DateTime
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from datetime import datetime

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
    __tablename__ = "house_pool"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    ip: Mapped[str] = mapped_column(String(30))
    hd_data: Mapped[list["HDData"]] = relationship(back_populates="house")
    actions: Mapped[list["ActionPool"]] = relationship(back_populates="house")

class HDData(Base):
    __tablename__ = "hd_data"

    id: Mapped[int] = mapped_column(primary_key=True)
    device_state: Mapped[int] = mapped_column(Integer())
    power_usage: Mapped[float] = mapped_column(Float())
    temperature: Mapped[float] = mapped_column(Float())
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    house_id: Mapped[int] = mapped_column(ForeignKey("house_pool.id"))
    house: Mapped["HousePool"] = relationship(back_populates="hd_data")

class ActionPool(Base):
    __tablename__ = "action_pool"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    house_id: Mapped[int] = mapped_column(ForeignKey("house_pool.id"))
    house: Mapped["HousePool"] = relationship(back_populates="actions")

if __name__ == "__main__":
    Base.metadata.create_all(engine)
