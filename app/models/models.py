from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
#from sqlalchemy.ext.declarative import declarative_base
from app.core.database import Base
from enum import Enum
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone_number = Column(Integer,  unique=False, nullable=False)
    user_password = Column(String, unique=True, nullable=False)
    role = Column(String, nullable=False)  # "listener" или "organization"
    verified = Column(Boolean, nullable=False)  # для organization - подтверждение записи
    # подтверждение будет происходить вручную после регистрации организации администратором сервиса

    #records = relationship("Record", back_populates="user")

class ConcertStatus(str, Enum):
    UPCOMING = "upcoming"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Concert(Base):
    __tablename__ = "concerts"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    description = Column(Text)
    price_type = Column(String)  # "free", "fixed", "hat"
    price_amount = Column(Integer, nullable=True)
    #max_people = Column(Integer)
    #current_people = Column(Integer, default=0)
    location = Column(String, nullable=False)
    current_status: ConcertStatus = Column(String, default=ConcertStatus.UPCOMING)
    organization_id = Column(Integer, ForeignKey("users.id"))

    organization = relationship("User")
    #records = relationship("Record", back_populates="concert")
    concert_composers = relationship("ConcertComposer", back_populates="concert")
    concert_instruments = relationship("ConcertInstrument", back_populates="concert")


class Composer(Base):
    __tablename__ = "composers"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    birth_year = Column(Integer)
    death_year = Column(Integer)

    concert_composers = relationship("ConcertComposer", back_populates="composer")


class Instrument(Base):
    __tablename__ = "instruments"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    concert_instruments = relationship("ConcertInstrument", back_populates="instrument")


#class Record(Base):
#    __tablename__ = "records"
#
#    id = Column(Integer, primary_key=True)
#    user_id = Column(Integer, ForeignKey("users.id"))
#    concert_id = Column(Integer, ForeignKey("concerts.id"))
#    attended = Column(Boolean, default=False)
#
#    user = relationship("User", back_populates="records")
#    concert = relationship("Concert", back_populates="records")


class ConcertComposer(Base):
    __tablename__ = "concert_composers" # many-to-many table for relation of concerts and composers

    id = Column(Integer, primary_key=True)
    concert_id = Column(Integer, ForeignKey("concerts.id"))
    composer_id = Column(Integer, ForeignKey("composers.id"))

    concert = relationship("Concert", back_populates="concert_composers")
    composer = relationship("Composer", back_populates="concert_composers")


class ConcertInstrument(Base):
    __tablename__ = "concert_instruments" # many-to-many table for relation of concerts and instruments

    id = Column(Integer, primary_key=True)
    concert_id = Column(Integer, ForeignKey("concerts.id"))
    instrument_id = Column(Integer, ForeignKey("instruments.id"))

    concert = relationship("Concert", back_populates="concert_instruments")
    instrument = relationship("Instrument", back_populates="concert_instruments")