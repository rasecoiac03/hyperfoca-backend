# importando as libs
from flask import Flask, request, jsonify
from flask_restful import Resource, Api, abort
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey
from json import dumps

data_base = create_engine('sqlite:///exemplo.db')
app = Flask(__name__)
api = Api(app)


def create_db_tables():
    metadata = MetaData()
    users = Table("user", metadata,
                    Column('id', Integer, primary_key=True),
                    Column('name', String),
                    Column('email', String),
                    Column('password', String)
                )
    try:
        metadata.create_all(data_base.connect())
        print("Tables created")
    except Exception as e:
        print("Error occurred during Table creation!")
        print(e)


# Endpints de Usuário: GET POST e PUT
class Users(Resource):
    def get(self):
        conn = data_base.connect()

        if 'email' in request.args:
            email = request.args['email']
            return jsonify(get_user_by_email(email))

        sql_query = "select * from user"
        query = conn.execute(sql_query)
        result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
        return jsonify(result)

    def post(self):
        conn = data_base.connect()
        name = request.json['name']
        email = request.json['email']
        password = request.json['password']

        user = conn.execute(
            "insert into user values(null, '{0}', '{1}', '{2}')".format(name, email, password))

        query = conn.execute('select * from user order by id desc limit 1')
        result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]   
        return jsonify(result)

    def put(self):
        conn = data_base.connect()
        id = request.json['id']
        name = request.json['name']
        email = request.json['email']

        conn.execute("update user set name ='" + str(name) + 
                        "', email ='" + str(email) +  "' where id = %d " % int(id))

        query = conn.execute("select * from user where id=%d" % int(id))
        result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor] 
        return jsonify(result)

# Endpints de envio de ID: GET e DELETE
class UserById(Resource):
    def delete(self, id):
        conn = data_base.connect()
        conn.execute("delete from user where id=%d" % int(id))
        return {"status": "success"}

    def get(self, id):
        user = get_user_by_id(id)
        if not user:
            abort(404)
        return jsonify(user)


def get_user_by_id(id):
    sql_query = f"select * from user where id = {int(id)}"
    return get_user(sql_query)

def get_user_by_email(email):
    sql_query = f"select * from user where email = '{email}'"
    return get_user(sql_query)

def get_user(sql_query):
    conn = data_base.connect()
    query = conn.execute(sql_query)
    result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor] 
    return result[0] if result else []

api.add_resource(Users, '/users')
api.add_resource(UserById, '/users/<id>')

if __name__ == '__main__':
    create_db_tables()
    app.run()
