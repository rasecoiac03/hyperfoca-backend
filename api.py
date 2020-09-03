# importando as libs
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps

data_base = create_engine('sqlite:///exemplo.db')
app = Flask(__name__)
api = Api(app)


# Endpints de Usuário: GET POST e PUT
class Users(Resource):
    def get(self):
        conn = data_base.connect()
        query = conn.execute("select * from user")
        result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
        return jsonify(result)

    def post(self):
        conn = data_base.connect()
        name = request.json['name']
        email = request.json['email']

        conn.execute(
            "insert into user values(null, '{0}'), '{1}')".format(name, email))

        query = conn.execute('select * from  user order by id desc limit 1')
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
        conn = data_base.connect()
        query = conn.execute("select * from users where id =%d " % int(id))
        result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor] 
        return jsonify(result)

api.add_resource(Users, '/users')
api.add_resource(UserById, '/users/<id>')

if __name__ == '__main__':
    app.run()



