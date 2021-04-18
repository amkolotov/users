import enum

import aiopg.sa
from sqlalchemy import MetaData, Table, Column, Integer, String, Boolean, ForeignKey, Date
from sqlalchemy_utils import ChoiceType

TYPES = [
    ('admin', 'Admin'),
    ('readonly', 'Readonly'),
]


class PermEnum(enum.Enum):
    ADMIN = 'admin'
    READONLY = 'readonly'


meta = MetaData()


users = Table(
    'users', meta,

    Column('id', Integer, primary_key=True),
    Column('login', String(128), nullable=False, unique=True),
    Column('password', String(128), nullable=False),
    Column('first_name', String(128)),
    Column('last_name', String(128)),
    Column('birthday', Date, nullable=True),
    Column('disabled', Boolean, nullable=False, default=False)
)

permissions = Table(
    'permissions', meta,

    Column('id', Integer, primary_key=True),
    Column('users_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), unique=True),
    Column('role', ChoiceType(PermEnum, impl=String()), nullable=False, default=PermEnum.READONLY.value),
    Column('blocking', Boolean, default=False)
)


async def init_pg(app):
    conf = app['config']['postgres']
    engine = await aiopg.sa.create_engine(
        database=conf['database'],
        user=conf['user'],
        password=conf['password'],
        host=conf['host'],
        port=conf['port'],
        minsize=conf['minsize'],
        maxsize=conf['maxsize'],
    )
    app['db'] = engine


async def close_pg(app):
    app['db'].close()
    await app['db'].wait_closed()





