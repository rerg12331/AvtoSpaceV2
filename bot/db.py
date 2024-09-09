from config import db_host, db_name, db_password, db_user
from sqlalchemy import create_engine, Column, Integer, String, BigInteger, Float, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
# Создание базы данных URL
DATABASE_URL = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:5432/{db_name}"

# Создание движка SQLAlchemy
engine = create_engine(DATABASE_URL)

# Создание базового класса для моделей
Base = declarative_base()

# Определение модели таблицы
class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(BigInteger, primary_key=True)
    name = Column(String(100))
    username = Column(String(100))
    chat_id = Column(BigInteger)
    location_latitude = Column(Float)
    location_longitude = Column(Float)
    date_registered = Column(DateTime, default=datetime.utcnow)

class Location(Base):
    __tablename__ = 'locations_users'
    user_id = Column(BigInteger, primary_key=True)
    data = Column(JSONB)

# Создание таблиц в базе данных (если они еще не существуют)
Base.metadata.create_all(engine)

# Создание сессии
Session = sessionmaker(bind=engine)
session = Session()