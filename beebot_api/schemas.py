import sqlalchemy as sa
from db_session import Base
import datetime


def as_dict(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}


Base.as_dict = as_dict


class User(Base):
    __tablename__ = 'users'
    telegram_id = sa.Column(sa.Integer, primary_key=True, unique=True, nullable=False)
    balance = sa.Column(sa.Integer, default=0)
    last_check = sa.Column(sa.DateTime, default=datetime.datetime.now())


class Lands(Base):
    __tablename__ = 'lands'
    telegram_id = sa.Column(sa.Integer, sa.ForeignKey('users.telegram_id'), primary_key=True, unique=True)
    flower_land = sa.Column(sa.Integer, default=1)
    forest_land = sa.Column(sa.Integer, default=0)
    mountain_land = sa.Column(sa.Integer, default=0)


class Bees(Base):
    __tablename__ = 'bees'
    telegram_id = sa.Column(sa.Integer, sa.ForeignKey("users.telegram_id"), primary_key=True, unique=True)
    regular_bees = sa.Column(sa.Integer, default=100)
    blue_bees = sa.Column(sa.Integer, default=0)


class Beehives(Base):
    __tablename__ = 'beehives'
    telegram_id = sa.Column(sa.Integer, sa.ForeignKey("users.telegram_id"), primary_key=True, unique=True)
    small_beehives = sa.Column(sa.Integer, default=1)
    medium_beehives = sa.Column(sa.Integer, default=0)
    large_beehives = sa.Column(sa.Integer, default=0)


class Honey(Base):
    __tablename__ = 'honey'
    telegram_id = sa.Column(sa.Integer, sa.ForeignKey("users.telegram_id"), primary_key=True, unique=True)
    honey = sa.Column(sa.Integer, default=0)
