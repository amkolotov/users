import json
from datetime import datetime

from aiohttp import web
from aiohttp_apispec import request_schema, docs, response_schema

from aiohttp_security import (
    remember, forget, authorized_userid,
    check_permission, check_authorized,
)
from passlib.handlers.sha2_crypt import sha256_crypt

from db_auth import check_credentials


import db
from schemas import UserSchema, LoginSchema, ResponseSchema, ResponseUsersSchema, ResponseUserSchema, \
    ResponseSchema, UserEditSchema


async def get_data(request):
    """Метод для получения данных из request"""
    if request.content_type == 'application/json':
        data = await request.text()
        data = json.loads(data)
        return data
    elif request.content_type == 'multipart/form-data':
        data = await request.post()
        return data


class Web(object):

    @docs(tags=['list'],
          summary='Список пользователей',
          description='Получение списка пользователей, доступно любому пользователю')
    @response_schema(ResponseUsersSchema(), 200)
    async def index(self, request):

        async with request.app.db_engine.acquire() as conn:
            cursor = await conn.execute(db.users.select())
            records = await cursor.fetchall()
            fields = ['id', 'login', 'first_name', 'last_name']
            users = [{field: record[field] for field in fields} for record in records]

            return web.json_response(users)

    @docs(tags=['detail'],
          summary='Информация о пользователе',
          description='Получение детальной информации о пользователе, доступно только администратору')
    @response_schema(ResponseUserSchema())
    async def detail(self, request):
        """Обработчик для получения детальной информации о пользователе"""
        await check_permission(request, 'admin')

        user_id = request.match_info.get('user_id')

        if user_id and user_id.isdigit():
            async with request.app.db_engine.acquire() as conn:
                try:
                    cursor = await conn.execute(db.users.select().where(db.users.c.id == user_id))
                    user = await cursor.fetchone()
                    response = dict(user)
                    try:
                        response['birthday'] = datetime.strftime(response['birthday'], '%d-%m-%Y')
                    except:
                        pass
                    status = 200
                except Exception as e:
                    response = {'error': str(e)}
                    status = 400

                return web.json_response(response, status=status)

    @docs(tags=['create'],
          summary='Создание нового пользователя',
          description='Право создания пользователя предоставлено только администратору')
    @request_schema(UserSchema())
    @response_schema(ResponseSchema())
    async def create(self, request):

        await check_permission(request, 'admin')

        data = await get_data(request)
        if data['login'] and data['password']:
            data = dict(data)
            data['password'] = sha256_crypt.hash(data['password'])
            async with request.app.db_engine.acquire() as conn:
                try:
                    cursor = await conn.execute(db.users.insert().values(**data))
                    response = {'message': 'success'}
                    status = 201
                except Exception as e:
                    response = {'error': str(e)}
                    status = 400

                return web.json_response(response, status=status)

    @docs(tags=['edit'],
          summary='Редактирование пользователя',
          description='Право редактирования пользователя предоставлено только администратору')
    @request_schema(UserEditSchema())
    @response_schema(ResponseSchema())
    async def edit(self, request):

        await check_permission(request, 'admin')

        user_id = request.match_info.get('user_id')
        data = await get_data(request)

        if user_id and user_id.isdigit() and data:
            async with request.app.db_engine.acquire() as conn:
                try:
                    await conn.execute(db.users.update().where(db.users.c.id == user_id).values(**data))
                    response = {'message': 'success'}
                    status = 201
                except Exception as e:
                    response = {'error': str(e)}
                    status = 400

                return web.json_response(response, status=status)

    @docs(tags=['delete'],
          summary='Удаление пользователей',
          description='Право удаления пользователя предоставлено только администратору')
    @response_schema(ResponseSchema())
    async def delete(self, request):

        await check_permission(request, 'admin')

        user_id = request.match_info.get('user_id')
        if user_id and user_id.isdigit():
            async with request.app.db_engine.acquire() as conn:
                try:
                    await conn.execute(db.users.delete().where(db.users.c.id == user_id))
                    response = {'message': 'success'}
                    status = 201
                except Exception as e:
                    response = {'error': str(e)}
                    status = 400

                return web.json_response(response, status=status)

    @docs(tags=['hoami'],
          summary='Проверка авторизации пользователя',
          description='Возвращает имя пользователя, если он авторизован')
    @response_schema(ResponseSchema())
    async def user(self, request):
        username = await authorized_userid(request)
        if username:
            message = f'Hello, {username}!'
            status = 200
        else:
            message = 'You need to login'
            status = 401

        return web.json_response({'message': message}, status=status)

    @docs(tags=['login'],
          summary='Аутентификация пользователя',
          description='Аутентификация пользователя и добавление идентификатора в cookies')
    @request_schema(LoginSchema())
    @response_schema(ResponseSchema())
    async def login(self, request):

        data = await get_data(request)

        if data and data['login'] and data['password']:
            login = data.get('login')
            password = data.get('password')
            db_engine = request.app.db_engine

            if await check_credentials(db_engine, login, password):
                response = web.json_response({'message': 'Вы вошли в систему'})
                await remember(request, response, login)
                return response

            raise web.HTTPUnauthorized(text=json.dumps({'error': 'Invalid username/password combination'}))

    @docs(tags=['logout'],
          summary='Выход пользователя',
          description='Удаление идентификатора пользователя из cookies')
    @response_schema(ResponseSchema())
    async def logout(self, request):
        await check_authorized(request)
        response = web.json_response({'message': 'Вы вышли из системы'})
        await forget(request, response)
        return response

    def configure(self, app):
        router = app.router
        router.add_route('GET', '/', self.index, name='index')
        router.add_route('GET', '/detail/{user_id}', self.detail, name='detail')
        router.add_route('POST', '/create', self.create, name='create')
        router.add_route('POST', '/edit/{user_id}', self.edit, name='edit')
        router.add_route('DELETE', '/delete/{user_id}', self.delete, name='delete')
        router.add_route('GET', '/user', self.user, name='user')
        router.add_route('POST', '/login', self.login, name='login')
        router.add_route('GET', '/logout', self.logout, name='logout')
