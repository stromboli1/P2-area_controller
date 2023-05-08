from sqlalchemy import String, Integer, Float, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

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
    timestamp: Mapped[int] = mapped_column(Integer())
    house_id: Mapped[int] = mapped_column(ForeignKey("house_pool.id"))

class ActionPool(Base):
    __tablename__ = "action_pool"

    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[int] = mapped_column(Integer())
    device: Mapped[int] = mapped_column(Integer())
    state_change: Mapped[bool] = mapped_column(Boolean())
    house_id: Mapped[int] = mapped_column(ForeignKey("house_pool.id"))
