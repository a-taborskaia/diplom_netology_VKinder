from sqlalchemy import create_engine, MetaData, Integer, Column, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from pprint import pprint
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
# Таблица искателей
class User(Base):
    __tablename__ = 'users'
    id_user = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, unique=True)
# Таблица с кандидатами, уже предлагаемыми пользователю
class Search(Base):
    __tablename__ = 'search'
    id_search = Column(Integer, primary_key=True)
    id_user = Column(Integer, ForeignKey("users.id_user"))
    user_search = Column(Integer, nullable=False, unique=True)

# Создание таблиц (выполнили один раз, не стала вствлять в основной код):
Base.metadata.create_all(engine)
# Добавление данных в таблицу, если пользователя нет - функция вернет TRUE
def write_db(user_id, user_search, session: sessionmaker):
    not_user = False
    user = session.query(User).filter_by(user_id=user_id).scalar()
    if not user:
        user = User(user_id=user_id)
    session.add(user)

    search = session.query(Search).join(User).filter(User.user_id == user_id, Search.user_search == user_search).scalar()
    if not search:
        not_user = True
        search = Search(id_user = user.id_user, user_search = user_search)
    session.add(search)
    session.commit()
    session.close()
    return not_user
