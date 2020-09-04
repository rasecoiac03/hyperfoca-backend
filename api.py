# importando as libs
from flask import Flask, request, jsonify
from flask_restful import Resource, Api, abort
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, Float
from json import dumps
import time


data_base = create_engine('sqlite:///exemplo.db')
app = Flask(__name__)
api = Api(app)


def create_db_tables():
    metadata = MetaData()
    users = Table('user', metadata,
                    Column('id', Integer, primary_key=True),
                    Column('name', String),
                    Column('email', String),
                    Column('password', String)
                )
    job_vacancies = Table('job_vacancy', metadata,
                    Column('id', Integer, primary_key=True),
                    Column('title', String),
                    Column('company', String),
                    Column('location', String),
                    Column('created_at', Float)
                )
    try:
        metadata.create_all(data_base.connect())
        print('Tables created')
    except Exception as e:
        print('Error occurred during Table creation!')
        print(e)


class Users(Resource):
    def get(self):
        conn = data_base.connect()

        if 'email' in request.args:
            email = request.args['email']
            result = get_user_by_email(email)
            if not result:
                abort(404)
            return jsonify(result)

        sql_query = 'select * from user'
        query = conn.execute(sql_query)
        result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
        return jsonify(result)

    def post(self):
        conn = data_base.connect()
        name = request.json['name']
        email = request.json['email']
        password = request.json['password']

        if get_user_by_email(email):
            abort(409)

        user_result = conn.execute(
            f'insert into user values(null, \'{name}\', \'{email}\', \'{password}\')')

        user = request.json
        user['id'] = user_result.lastrowid

        return jsonify(user)

    def put(self):
        conn = data_base.connect()
        id = request.json['id']
        name = request.json['name']
        email = request.json['email']

        conn.execute(f'update user set name = \'{name}\', email = \'{email}\' where id = {int(id)}')

        query = conn.execute(f'select * from user where id= {int(id)}')
        result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor] 
        return jsonify(result)


class UserById(Resource):
    def delete(self, id):
        conn = data_base.connect()
        conn.execute(f'delete from user where id= {int(id)}')
        return {'status': 'success'}

    def get(self, id):
        user = get_user_by_id(id)
        if not user:
            abort(404)
        return jsonify(user)


class JobVacancies(Resource):
    def post(self):
        conn = data_base.connect()
        title = request.json['title']
        company = request.json['company']
        location = request.json['location']
        created_at = time.time()
        job_vacancy_result = conn.execute(
            f'insert into job_vacancy values(null, \'{title}\', \'{company}\', \'{location}\', {created_at})')

        job_vacancy = request.json
        job_vacancy['id'] = job_vacancy_result.lastrowid

        return jsonify(job_vacancy)

    def get(self):
        conn = data_base.connect()
        sql_query = 'select * from job_vacancy'
        query = conn.execute(sql_query)
        result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
        return jsonify(result)


class JobVacanciesById(Resource):
    def delete(self, id):
        conn = data_base.connect()
        conn.execute(f'delete from user job_vacancy id = {int(id)}')
        return {'status': 'success'}

    def get(self, id):
        sql_query = f'select * from job_vacancy where id = {int(id)}'
        job_vacancy = get_row(sql_query)
        if not job_vacancy:
            abort(404)
        return jsonify(job_vacancy)


def get_user_by_id(id):
    sql_query = f'select * from user where id = {int(id)}'
    return get_row(sql_query)

def get_user_by_email(email):
    sql_query = f'select * from user where email = \'{email}\''
    return get_row(sql_query)

def get_row(sql_query):
    conn = data_base.connect()
    query = conn.execute(sql_query)
    result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor] 
    return result[0] if result else []


api.add_resource(Users, '/users')
api.add_resource(UserById, '/users/<id>')
api.add_resource(JobVacancies, '/jobs')
api.add_resource(JobVacanciesById, '/jobs/<id>')

if __name__ == '__main__':
    create_db_tables()
    app.run()
