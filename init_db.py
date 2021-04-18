from datetime import datetime

from passlib.handlers.sha2_crypt import sha256_crypt
from sqlalchemy import MetaData, create_engine

from my_app.settings import config
from my_app.db import users, permissions, PermEnum


DSN = "postgresql://{user}:{password}@{host}:{port}/{database}"


def create_tables(engine):
    meta = MetaData()
    tables = [permissions, users]
    for table in tables:
        if engine.dialect.has_table(engine, table):
            meta.drop_all(bind=engine, tables=[table])
    meta.create_all(bind=engine, tables=[users, permissions])


def sample_data(engine):
    admin_pass = sha256_crypt.hash('admin')
    user_pass = sha256_crypt.hash('user')
    conn = engine.connect()
    conn.execute(users.insert(), [
        {'login': 'admin',
         'password': admin_pass,
         'first_name': 'admin',
         'last_name': 'admin',
         'birthday': datetime.strptime('01-01-1970', '%d-%m-%Y').date()
         },

        {'login': 'user',
         'password': user_pass,
         'first_name': 'user',
         'last_name': 'user',
         'birthday': datetime.strptime('11-11-2001', '%d-%m-%Y').date()
         },

    ])
    conn.execute(permissions.insert(), [
        {'users_id': 1, 'role': PermEnum.ADMIN},
        {'users_id': 2, 'role': PermEnum.READONLY},
    ])
    conn.close()


if __name__ == '__main__':
    db_url = DSN.format(**config['postgres'])
    engine = create_engine(db_url)

    create_tables(engine)
    sample_data(engine)
