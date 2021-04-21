import enum
from typing import Union

import sqlalchemy as sa

from aiohttp_security.abc import AbstractAuthorizationPolicy
from passlib.hash import sha256_crypt

import db


class DBAuthorizationPolicy(AbstractAuthorizationPolicy):
    def __init__(self, db_engine):
        self.db_engine = db_engine

    async def authorized_userid(self, identity: str) -> Union[str, None]:
        """Проверка авторизации пользователя"""
        async with self.db_engine.acquire() as conn:
            where = sa.and_(db.users.c.login == identity,
                            sa.not_(db.users.c.disabled))
            query = db.users.count().where(where)
            ret = await conn.scalar(query)
            if ret:
                return identity
            else:
                return None

    async def permits(self, identity: Union[str, None], permission: str, context=None) -> bool:
        """Проверка наличия права у пользователя"""
        if not identity:
            return False

        async with self.db_engine.acquire() as conn:
            where = sa.and_(db.users.c.login == identity,
                            sa.not_(db.users.c.disabled))
            query = db.users.select().where(where)
            ret = await conn.execute(query)
            user = await ret.fetchone()
            if user:
                user_id = user[0]
                where = db.permissions.c.users_id == user_id
                query = db.permissions.select().where(where)
                ret = await conn.execute(query)
                result = await ret.fetchone()
                if result:
                    if result.role.value == permission:
                        return True

            return False


async def check_credentials(db_engine, username: str, password: str) -> bool:
    """Проверка правильности пароля"""
    async with db_engine.acquire() as conn:
        where = sa.and_(db.users.c.login == username,
                        sa.not_(db.users.c.disabled))
        query = db.users.select().where(where)
        ret = await conn.execute(query)
        user = await ret.fetchone()
        if user:
            hashed = user.password
            return sha256_crypt.verify(password, hashed)
    return False
