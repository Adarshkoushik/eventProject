from sqlalchemy import Column, Integer, String, DateTime, text
from sqlalchemy.ext.declarative import declarative_base


# SQLAlchemy models
Base = declarative_base()

class Event(Base):
    __tablename__ = "events"

    event_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    event_title = Column(String, index=True)
    event_description = Column(String)
    event_date = Column(DateTime)
    event_location = Column(String)

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String, unique=True, index=True)
    lastname = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    address = Column(String)

class EventRegistration(Base):
    __tablename__ = "eventregistrations"

    registration_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    event_id = Column(Integer, index=True)
    registration_date = Column(DateTime, server_default=text("(now() at time zone 'UTC')"))
