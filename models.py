
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime

Base = declarative_base()

class Farmer(Base):
    __tablename__ = 'farmers'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20))
    location = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    farm_size = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class SoilTest(Base):
    __tablename__ = 'soil_tests'

    id = Column(Integer, primary_key=True)
    farmer_id = Column(Integer)
    test_date = Column(DateTime)
    n_percent = Column(Float)
    p_ppm = Column(Float)
    k_ppm = Column(Float)
    ph = Column(Float)
    organic_carbon = Column(Float)
    laboratory = Column(String(100))

class Recommendation(Base):
    __tablename__ = 'recommendations'

    id = Column(Integer, primary_key=True)
    farmer_id = Column(Integer)
    soil_test_id = Column(Integer)
    season = Column(String(50))
    n_rate = Column(Float)
    p_rate = Column(Float)
    k_rate = Column(Float)
    predicted_yield = Column(Float)
    cost_estimate = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class AdoptionTracking(Base):
    __tablename__ = 'adoption_tracking'

    id = Column(Integer, primary_key=True)
    farmer_id = Column(Integer)
    recommendation_id = Column(Integer)
    adopted = Column(Boolean)
    actual_yield = Column(Float)
    feedback = Column(String(500))
    season = Column(String(50))
    recorded_at = Column(DateTime, default=datetime.utcnow)
