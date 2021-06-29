#This is a test API which connects to MongoDB

from flask import Flask, jsonify, request
from flask_pymongo import PyMongo, ObjectId, MongoClient
from flask_cors import CORS, cross_origin
# from certifi import where
# import certifi
#from werkzeug.datastructures import Authorization
#from werkzeug.http import *
app = Flask(__name__)
#client = MongoClient("mongodb+srv://AlisaleeAaron:Pokebolt9898@testbox.yqkcy.mongodb.net", tlsCAFile=certifi.where())

#Configuration for root User

app.config['MONGO_URI'] = 'mongodb+srv://AlisaleeAaron:Pokebolt9898@testbox.yqkcy.mongodb.net/TestData?retryWrites=true&w=majority'
app.config['MONGO_DBNAME'] = 'TestData'

#Solves the CORS  No 'Access-Control-Allow-Origin' header is present problem
app.config['CORS_HEADERS'] = 'Content-Type'


mongo = PyMongo(app)
CORS(app, send_wildcard=True)

## End ##


### Configuration for requiring authentiecation ###
def get_mongo(request):
    Auth = request.authorization
    if Auth.username == "" or Auth.password == "":
        return None
    else:
        username = Auth.username
        password = Auth.password
        ConnectionString = 'mongodb+srv://' + username + ":" + password + '@testbox.yqkcy.mongodb.net/TestData?retryWrites=true&w=majority'
        app.config['MONGO_URI'] = ConnectionString
        #mongo = PyMongo.init_app(app=app, uri=ConnectionString)
        mongo = PyMongo(app)
        return mongo
        

### Here are methods to return values to badly typed URI's ###

@app.route("/")
def home():
    return jsonify({'message': "There is nothing here"})


@app.route('/Person/', methods=['GET'])
def no_person():
     return jsonify({'message': "Must Specify Name."})


@app.route('/delete/', methods=['DELETE'])
def no_name():
    return jsonify({'messge': 'Name required'})

@app.route('/Person', methods=['OPTIONS'])
def post_option():
    return jsonify({'message': "option called"})

####### End of Catching Methods #######

#request.args.get() allows for the aquisition of query args
#   these are preceeded by '?' at the end of the URI
@app.route("/People", methods=['GET'])
def get_people():
    # try:
    #     mongo = get_mongo(request)
        
        # assert(mongo != None)
        
        #request.json
        #return jsonify({'result': })

        data = mongo.db.People  
        output = []

        name_start = request.args.get('start_with')
        name_end = request.args.get('end_with')
        
        if name_start == None:
            for person in data.find():
                output.append({'id': person['_id'].__str__(), 'name' : person['name'], 'start_date': person['start_date'], 'end_date': person['end_date'], 'utilities': person['utilities'],  'owed': person['owed']})
        else:
            #The carrot '^' at the begining means that the value of name_start
            #   must appear at the begining of the name
            for person in data.find({'name': {"$regex": ("^" + name_start)}}):
                output.append({'id': person['_id'].__str__(), 'name' : person['name'], 'start_date': person['start_date'], 'end_date': person['end_date'], 'utilities': person['utilities'],  'owed': person['owed']})
        
        return jsonify(output)
    # except AssertionError:
    #     return jsonify({'message': 'Improper Authorization Credentials'})


@app.route('/Person/<id>', methods=['GET'])
def get_person(id):
    #try:
        # mongo = get_mongo(request)
        # assert(mongo != None)
        
        data = mongo.db.People

        found = data.find_one({"_id": ObjectId(id)})

        if(found):
            result = {"name": found["name"], "start_date": found["start_date"], "utilities": found["utilities"]}
            return jsonify(result)
        else:
            return jsonify( {'message': ('Person' + " not found. Try again!")})
    # except AssertionError:
    #     return jsonify({'message': 'Improper Authorization Credentials'})

@app.route('/Person', methods=['POST'])
@cross_origin()
def add_person():
    # try:
        #eg: {"name": "Lemmy", "start_date": "Wed, 16 Jun 05:00:00 GMT", "end_date": "Mon, 13 Dec 05:00:00 GMT", "utilities": 54.59, "owed": 0}
        # mongo = get_mongo(request)
        # assert(mongo != None)
        data = mongo.db.People
        
        
        # The issue was not a CORS problem bc POST is a "simple" action and
        # should not requre preflight, the problem was that the request data was
        #not seen in JSON format, below forces the api to interpret is as JSON
        request.get_json(force=True)
        name = request.json['name']
        start_date = request.json['start_date']
        end_date = request.json['end_date']
        utilities = request.json['utilities']
        owed = request.json['owed']

        # Convert to date-time type, string --> ISO datetime
        inserted_id = data.insert({"name": name, "start_date": start_date, "end_date": end_date, "utilities": utilities, "owed": owed})
        new_person = data.find_one({"_id": inserted_id})

        return jsonify({'name': new_person['name'], 'start_date': new_person['start_date'], 'end_date': new_person['end_date'], 'utilities': new_person['utilities'],  'owed': new_person['owed']})
    #Find a way to catch a code 8000 Atlas Operation Error if unqualified person tries to do an action
    # except AssertionError:
    #     return jsonify({'message': 'Improper Authorization Credentials'})


#doing this makes the owed paramater optional
@app.route('/edit/<name>/<value>/<owed>', methods=['PATCH'])
@app.route('/edit/<name>/<value>', defaults={'owed' : None}, methods=['PATCH'])
def edit_utilities(name, value, owed):
    # try:
        # mongo = get_mongo(request)
        # assert(mongo != None)

        data = mongo.db.People
        if(owed == None):
            update_details = data.update_one({'name': name}, {"$set": {'utilities': value}})
        else:
            update_details = data.update_one({'name': name}, {"$set": {'utilities': value, 'owed': owed}})
        
        return jsonify({'message': "success"})

        #Find out a way to track what was updated --> below does not work
        # person_updated = data.find_one({'_id': update_details.upserted_id})

        # output = {'name': person_updated['name'], 'utilities': person_updated['utilities']}

        # return jsonify({"results": output})
    # except AssertionError:
    #     return jsonify({'message': 'Improper Authorization Credentials'})


@app.route('/delete/<name>', methods=['DELETE'])
def delete_person(name):
    # try:
        # mongo = get_mongo(request)
        # assert(mongo != None)

        data = mongo.db.People
        id = request.args.get('id')

        if id != None:
            person = data.find_one({"_id" : ObjectId(id)})
            if person:
                data.delete_one({"_id" : ObjectId(id)})
            else:
                return jsonify({'message': "Delete unsuccessful: Person not found"})
        else:
            person = data.find_one({'name': name})
            if person:
                data.delete_one({'name': name})
            else:
                return jsonify({'message': "Delete unsuccessful: Person not found"})
        
        #Wanted to return ID look into further

        output = {'name': person['name'], 'start_date': person['start_date'], 'end_date': person['end_date'], 'owed': person['owed']}
        
        return jsonify(output)#{'message': "sucessful deletion", 'result': output})
    # except AssertionError:
    #     return jsonify({'message': 'Improper Authorization Credentials'})


# @app.route('/Person/<name>', methods=['GET'])
# def get_person(name):
#     #try:
#         # mongo = get_mongo(request)
#         # assert(mongo != None)
        
#         data = mongo.db.People

#         found = data.find_one({"name": name})

#         if(found):
#             result = {"name": found["name"], "start_date": found["start_date"], "utilities": found["utilities"]}
#             return jsonify({"result" : result})
#         else:
#             return jsonify( {'message': (name + " not found. Try again!")})
#     # except AssertionError:
#     #     return jsonify({'message': 'Improper Authorization Credentials'})