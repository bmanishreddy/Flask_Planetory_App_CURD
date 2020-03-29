from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
import os
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager, jwt_required, create_access_token




app = Flask(__name__)
basdir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basdir,'planets.db')
app.config['JWT_SECRET_KEY'] = 'super-secret'
db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)




@app.cli.command('db_create')
def db_create():
    db.create_all()
    print("Db Created !")

@app.cli.command('db_drop')
def db_drop_all():
    db.drop_all()
    print("Db dropped!")

@app.cli.command('db_seed')
def db_seed():
    mercury = Planet(planet_name='Mercury',planet_type='ClassD'
                     ,home_star='sol',mass=3.258e23,radius=1516,
                     distance=35.98e6)
    venus = Planet(planet_name='venus', planet_type='Classk'
                     , home_star='sol', mass=4.556e23, radius=235234,
                     distance=33324.98e6)
    earth = Planet(planet_name='Earth', planet_type='Class M'
                   , home_star='sol', mass=5.972e23, radius=235234,
                   distance=2314123.98e6)
    db.session.add(mercury)
    db.session.add(venus)
    db.session.add(earth)

    test_user = User(first_name='Arya',last_name='bhatta',email='Test@test.com',password='p@1234')

    db.session.add(test_user)
    db.session.commit()
    print("Database seeded !")






@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/super_simple')
def super_simple():
    return jsonify(message = 'Hello from the planetery api ', china= 'corona virus') , 200



@app.route('/not_found')
def not_found():
    return  jsonify(message = 'app route not found ') , 404

@app.route('/parameters')
def parameters():
    name = request.args.get('name')
    age = int(request.args.get('age'))
    if age<18:
        return jsonify(message = "sorry "+name+"you are not old enough to enter ") ,401
    else:
        return jsonify(message= "welcome"+name+"its great seeing customers like you ")


@app.route('/url_varibles/<string:name>/<int:age>')
def url_varibles(name: str,age: int):
    if age<18:
        return jsonify(message = "sorry "+name+"you are not old enough to enter ") ,401
    else:
        return jsonify(message= "welcome"+name+"its great seeing customers like you ")

@app.route('/planets')
def planets():
    planets_list = Planet.query.all()
    #print('planet details', planets_list)
    #print('planet object type ', type(planets_list))
    result = planets_schema.dump(planets_list)
    return jsonify(result)


@app.route('/register',methods=['POST'])
def register():
    email = request.form['email']
    test = User.query.filter_by(email=email).first()
    if test:
        return jsonify(message = 'email already exists '), 409
    else:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']
        user = User(first_name=first_name,last_name=last_name,password=password,email=email)
        db.session.add(user)
        db.session.commit()
        return jsonify(message = 'user created sucessfully'), 201



@app.route('/login',methods=['POST'])
def login():
    if request.is_json:
        email = request.json['email']
        password = request.json['password']
    else:
        email = request.form['email']
        password = request.form['password']
    test = User.query.filter_by(email =email,password=password).first()
    if test:
        access_token = create_access_token(identity=email)
        return jsonify(message = "login suceeded ",access_token=access_token)
    else:
        return jsonify(message = "bad email password "), 401

@app.route('/planet_details/<int:planet_id>',methods=["GET"])
def planet_details(planet_id: int):
    planet = Planet.query.filter_by(planet_id=planet_id).first()

    #restult = planets_schema.dump(planet)
    if planet:

        print('planet details',planet)
        print('planet object type ',type(planet))
        restult = planets_schema.dump(planet)
        return jsonify(restult.data)
    else:
        return jsonify(message = "That planet does not exist "), 404



@app.route('/add_planet',methods=["POST"])
def add_planet():
    planet_name = request.form['planet_name']
    #print("Planent mname =======",planet_name)
    test = Planet.query.filter_by(planet_name=planet_name).first()
    #print("Planent mname +++++++", test)
    if test:
        return jsonify(message = 'There is already planet by that name '), 409
    else:
        planet_type = request.form['planet_type']
        home_star = request.form['home_star']
        mass = request.form['mass']
        radius = request.form['radius']
        distance = request.form['distance']

        new_planet = Planet(planet_type=planet_type,planet_name= planet_name,home_star=home_star,mass=mass,
                            radius=radius,distance=distance)

        db.session.add(new_planet)
        db.session.commit()
        return jsonify(message = "You added a planet "), 201



@app.route('/update_planet',methods=['PUT'])
def update_planet():
    planet_id = int(request.form['planet_id'])
    planet = Planet.query.filter_by(planet_id=planet_id).first()
    if planet:
        planet.planet_name = request.form['planet_name']
        planet.planet_type = request.form['planet_type']
        planet.home_star = request.form['home_star']
        planet.mass = request.form['mass']
        planet.radius = request.form['radius']
        planet.distance = request.form['distance']
        db.session.commit()
        return jsonify(message = "you updated a planet"), 202
    else:
        return jsonify(message="the planet does not existis"), 404


@app.route('/remove_planet/<int:planet_id>',methods=['DELETE'])
def remove_planet(planet_id: int):
    planet = Planet.query.filter_by(planet_id=planet_id).first()
    if planet:
        db.session.delete(planet)
        db.session.commit()
        return jsonify(message = 'you deleted a planet'), 202
    else:
        return jsonify(message = 'that planet does not exist'), 404





#database models
class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String,unique=True)
    password = Column(String)


class Planet(db.Model):
    __tablename__ = 'planets'
    planet_id = Column(Integer , primary_key=True)
    planet_name = Column(String)
    planet_type = Column(String)
    home_star = Column(String)
    mass = Column(String)
    radius = Column(String)
    distance = Column(String)


class UserSchema(ma.Schema):
    class Meta:
        fields = ('id','first_name','last_name','email','password')



class PlanetSchema(ma.Schema):
    class Meta:
        fields = ('planet_id','planet_name','planet_type','home_star','mass','radius','distance')

user_schema = UserSchema() #Getting a single object
user_schema = UserSchema(many=True) #Getting multiple objects

planets_schema = PlanetSchema()
planets_schema = PlanetSchema(many=True)



if __name__ == '__main__':
    app.run()
