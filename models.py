# coding: utf-8
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, Table, text, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata

class Appointment(Base):
    __tablename__ = 'appointment'

    appointment_id = Column(Integer, primary_key=True)
    date = Column(DateTime, server_default=func.now())
    name = Column(String(50))


