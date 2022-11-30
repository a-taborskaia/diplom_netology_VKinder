from sqlalchemy import create_engine, MetaData, Integer, Column, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
# Подключение к БД

def sql_connect():
    db = 'postgresql+psycopg2://postgres:zorro333@localhost:5432/VKinder'
    connect = create_engine(db)
    return connect

engine = sql_connect()

try:
    Session = sessionmaker(bind=sql_connect())
finally:
    sessionmaker.close_all()

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
    id_user = Column(Integer, ForeignKey("users.id_user"))

# Создание таблиц (выполнили один раз, не стала вствлять в основной код):
Base.metadata.create_all(engine)

def write_client_id(user_id, session: sessionmaker):
    # session = Session
    client = session.query(Client).filter_by(user_id = user_id).scalar()
    if not client:
        client = Client(user_id = user_id)
    session.add(client)
    session.commit()
    session.close()

def write_user_id(user_id, session: sessionmaker):
    # session = Session
    user = session.query(User).filter_by(user_id = user_id).scalar()
    if not user:
        user = User(user_id = user_id)
    session.add(user)
    session.commit()
    session.close()

def write_kinder(user_id, client_id, session: sessionmaker):
    # session = Session
    kinder= session.query(Kinder).filter(and_(id_client == client_id,
                                               id_user == user_id)).scalar()
    if not kinder:
        kinder = Kinder(id_client = client_id,
                        id_user = user_id)
    session.add(kinder)
    session.commit()
    session.close()

