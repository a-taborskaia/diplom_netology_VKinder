from sqlalchemy import create_engine, MetaData, Integer, Column, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
# Подключение к БД
db = 'postgresql+psycopg2://postgres:zorro333@localhost:5432/VKinder'
engine = create_engine(db)
connection = engine.connect()

Base = declarative_base()
metadata = MetaData()

# Создание таблиц:
class Client(Base):
    __tablename__ = 'clients'
    id_client = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, unique=True)

class User(Base):
    __tablename__ = 'users'
    id_user = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, unique=True)

class Kinder(Base):
    __tablename__ = 'kinders'
    id_kinder = Column(Integer, primary_key=True)
    id_client = Column(Integer, ForeignKey("clients.id_client"))
    user_id = Column(Integer, ForeignKey("users.id_user"))

Base.metadata.create_all(engine)

