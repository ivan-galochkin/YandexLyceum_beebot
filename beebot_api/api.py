from fastapi import FastAPI, Header, HTTPException
import fastapi
from item_models import UserItem
from db_session import create_session, global_init
from schemas import *
import sqlalchemy as sa
from os import environ
import datetime as dt
import constants
import uvicorn
import json

app = FastAPI()

API_TOKEN = environ["API_TOKEN"]

table_names = {
    'user': User,
    'lands': Lands,
    'bees': Bees,
    'beehives': Beehives,
    'honey': Honey
}

unstable_values = {
    Honey: Honey.honey
}

stable_values = {
    'blue_bees': Bees.blue_bees,
    'regular_bees': Bees.regular_bees,
    'flower_land': Lands.forest_land,
    'small_beehives': Beehives.small_beehives,
    'medium_beehives': Beehives.medium_beehives,
    'large_beehives': Beehives.large_beehives,
}


def configure_user(item: UserItem):
    user = User()
    user.telegram_id = item.telegram_id
    user.lands = [Lands()]
    user.bees = [Bees()]
    user.beehives = [Beehives()]
    user.honey = [Honey()]
    return user


def get_time_delta(telegram_id):
    session = create_session()
    try:
        time_now = dt.datetime.now()

        time_last_check = session.query(User).filter(User.telegram_id == telegram_id).one().last_check

        time_delta = time_now - time_last_check

        return time_delta.total_seconds()
    finally:
        session.close()


def get_bees(telegram_id):
    session = create_session()
    try:
        bees = session.query(Bees).filter(Bees.telegram_id == telegram_id).one()
        return [bees.regular_bees, bees.blue_bees]
    finally:
        session.close()


def update_unstable_values(telegram_id):
    time_delta = get_time_delta(telegram_id)
    bees = get_bees(telegram_id)
    accumulated = (bees[0] * constants.REGULAR_BEE_HPS + bees[1] * constants.BLUE_BEE_HPS) * time_delta
    session = create_session()
    try:
        for table in unstable_values.keys():
            session.query(table).filter(table.telegram_id == telegram_id).update(
                {unstable_values[table]: unstable_values[table] + accumulated})
        session.query(User).filter(User.telegram_id == telegram_id).update({User.last_check: dt.datetime.now()})
        session.commit()
    finally:
        session.close()


def sell_honey(telegram_id):
    try:
        session = create_session()
        data = session.query(Honey).filter(Honey.telegram_id == telegram_id).one()
        income = data.honey * constants.REGULAR_HONEY_COST
        session.query(Honey).filter(Honey.telegram_id == telegram_id).update({"honey": 0})
        session.query(User).filter(User.telegram_id == telegram_id).update({User.balance: User.balance + income})
        session.commit()
    finally:
        session.close()


def buy_item(telegram_id, table_name, item, count):
    try:
        session = create_session()

        if "bee" in item and "hive" not in item:
            beehives = session.query(Beehives).filter(Beehives.telegram_id == telegram_id).one()
            all_beehives = beehives.small_beehives + beehives.medium_beehives + beehives.large_beehives
            bee_count = sum(get_bees(telegram_id))
            if all_beehives < bee_count / 100 + 1:
                return 'Not enough storage'

        cash = session.query(User).filter(User.telegram_id == telegram_id).one().balance

        price = constants.ITEM_PRICES[item] * count

        if price > cash:
            return "Not enough cash"

        table = table_names[table_name]
        session.query(table).filter(table.telegram_id == telegram_id).update(
            {getattr(table, item): getattr(table, item) + count})
        session.query(User).filter(User.telegram_id == telegram_id).update({User.balance: cash - price})

        session.commit()
        return "200"
    finally:
        session.close()


@app.put('/users')
def update_userdata(telegram_id: int, table_name: str, item: str, count: int, mode: str, token=Header(None)):
    if token:
        if table_name == "unstable":
            update_unstable_values(telegram_id)
        else:
            if mode == "sell":
                sell_honey(telegram_id)
            elif mode == "buy":
                response = buy_item(telegram_id, table_name, item, count)
                return response


@app.get('/users')
def get_userdata(telegram_id: int, table_name: str, token=Header(None)):
    """
    :param telegram_id: телехрам айди
    :param table_name: название таблицы
    :param token: токен
    :return:
    """
    if token == API_TOKEN:
        session = create_session()
        try:

            data = session.query(table_names[table_name]).filter(
                table_names[table_name].telegram_id == telegram_id).one()
            session.commit()
            return data.as_dict()
        finally:
            session.close()
    else:
        return HTTPException(401, "INVALID TOKEN")


@app.post("/users")
def create_user(item: UserItem, token=Header(None)):
    if token == API_TOKEN:
        try:
            session = create_session()

            user = configure_user(item)

            session.add(user)
            session.commit()

            return fastapi.responses.Response(status_code=200)
        except sa.exc.IntegrityError as exc:
            raise HTTPException(status_code=409,
                                detail={'exception': "UniqueError",
                                        'column': str(exc.orig).split(' ')[-1]})
        finally:
            session.close()
    else:
        raise HTTPException(401, "INVALID TOKEN")


global_init('users.sqlite')

uvicorn.run(app, host="127.0.0.1", port=8000)
