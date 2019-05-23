# coding: utf-8
from sqlalchemy import (
    Column, DateTime, ForeignKey, Integer, Numeric, String, Table, text, func, Boolean
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata

class Appointment(Base):
    __tablename__ = 'appointment'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, server_default=func.now())
    patient_name = Column(String(50), nullable=False)
    doctor_id = Column(ForeignKey('doctor.id'), nullable=False, index=True)
    service_id = Column(ForeignKey('service.id'), nullable=False, index=True)
    price_id = Column(ForeignKey('price.id'))
    custom_price = Column(Numeric(10,2))
    payment = Column(String(30), nullable=False)
    referral = Column(Integer)
    referral_accepted = Column(String(2))
    pzu = Column(Integer)

    doctor = relationship('Doctor')
    service = relationship('Service')
    price = relationship('PriceList')


class PriceList(Base):
    __tablename__ = 'price'

    id = Column(Integer, primary_key=True)
    doctor_id = Column(ForeignKey('doctor.id'), nullable=False, index=True)
    service_id = Column(ForeignKey('service.id'), nullable=False, index=True)
    price = Column(Numeric(10,2), nullable=False)

    doctor = relationship('Doctor')
    service = relationship('Service')

class Service(Base):
    __tablename__ = 'service'

    id = Column(Integer, primary_key=True)
    name = Column(String(60), nullable=False)

class Doctor(Base):
    __tablename__ = 'doctor'

    id = Column(Integer, primary_key=True)
    doctor_name = Column(String(50), nullable=False)
