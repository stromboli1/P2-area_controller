from sqlalchemy import String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from datetime import datetime

Base = declarative_base()

class HousePool(Base):
    __tablename__ = "house_pool"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    ip: Mapped[str] = mapped_column(String(30))

class HDData(Base):
    __tablename__ = "hd_data"

    id: Mapped[int] = mapped_column(primary_key=True)
    device_state: Mapped[int] = mapped_column(Integer())
    power_usage: Mapped[float] = mapped_column(Float())
    temperature: Mapped[float] = mapped_column(Float())
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    house_id: Mapped[int] = mapped_column(ForeignKey("house_pool.id"))

class ActionPool(Base):
    __tablename__ = "action_pool"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    house_id: Mapped[int] = mapped_column(ForeignKey("house_pool.id"))

