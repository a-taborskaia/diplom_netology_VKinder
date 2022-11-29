from sqlalchemy import create_engine
from sqlalchemy import MetaData, Table, ForeignKey, Integer, Column
# import psycopg2

db = 'postgresql+psycopg2://postgres:zorro333@localhost:5432/VKinder'
engine = create_engine(db)
connection = engine.connect()

def create_table():
    metadata = MetaData()

    client = Table('clients', metadata,
                   Column('id_client', Integer(), primary_key=True),
                   Column('user_id', Integer(), nullable=False, unique=True))
    users = Table('users', metadata,
                  Column('id_user', Integer(), primary_key=True),
                  Column('user_id', Integer(), nullable=False, unique=True))
    kinder = Table('kinder', metadata,
                   Column('id_kinder', Integer(), primary_key=True),
                   Column('client_id', ForeignKey("clients.id_client")),
                   Column('user_id', ForeignKey("users.id_user")))

    metadata.create_all(engine)
# Для запуска создания таблиц:
create_table()

# Создание таблиц через ORM:

