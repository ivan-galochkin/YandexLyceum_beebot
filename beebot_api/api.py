from fastapi import FastAPI, Header, HTTPException
import fastapi
from item_models import UserItem
from db_session import create_session, global_init
from schemas import *
import sqlalchemy as sa
from os import environ
import json

app = FastAPI()

API_TOKEN = environ["API_TOKEN"]

table_names = {
    'user': User,
    'lands': Lands,
    'bees': Bees,
    'behives': Beehives,
    'honey': Honey
}


@app.post("/users")
async def create_user(item: UserItem, token=Header(None)):
    if token == API_TOKEN:
        session = create_session()
        try:
            user = User()
            user.telegram_id = item.telegram_id
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


@app.get('/users')
async def get_money(telegram_id: int, table_name: str, token=Header(None)):
    if token == API_TOKEN:
        session = create_session()
        try:
            data = session.query(table_names[table_name]).filter(User.telegram_id == telegram_id).one()
            session.commit()
            return data.as_dict()
        finally:
            session.close()
    else:
        return HTTPException(401, "INVALID TOKEN")


global_init('users.sqlite')
