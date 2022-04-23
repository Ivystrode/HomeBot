from flask import Flask, json, request
from flask_cors import CORS
from pymongo import MongoClient

import os, sys
from decouple import config

"""
API for getting and posting new data to the MongoDB Atlas instance
"""

# ==========SETUP==========

db_pwd = config("mongo_db_pwd")

connection_string = f'mongodb+srv://main:{db_pwd}@cluster0.4yhee.mongodb.net'
client = MongoClient(connection_string, serverSelectionTimeoutMS=5000) 

# Database
db = client['testdb']

# Collections
detections = db.detections
temp = db.temperature_readings
co2 = db.co2_readings
cameras = db.cameras


# ==========FLASK API==========

app = Flask(__name__)
# CORS(app)
cors = CORS(app, resources={r'/*': {"origins": '*'}})
app.config['CORS_HEADER'] = 'Content-Type: application/json'

@app.route("/")
def hello():
    return "API is fucking working"

@app.route("/get/<requested_data>", methods=['GET'])
def get_data(requested_data):
    
    # there must be a better way of doing this
    if requested_data == "temp":
        collection = temp
    elif requested_data == "co2":
        collection = co2
    elif requested_data == "detections":
        collection = detections
    elif requested_data == "cameras":
        collection = cameras
        
    try:
        db_data = collection.find()
        print(db_data)
        response = []
        for item in db_data:
            item['_id'] = str(item['_id'])
            response.append(item)
            
        return json.dumps(response)
    
    except Exception as e:
        return e
    
# @app.route("/get/graphs", methods=['GET'])
# def get_graphs():
#     try:
#         graph_data = graphs.find()
#         response = []
#         for item in graph_data:
#             item['_id'] = str(item['_id'])
#             response.append(item)
            
#         return json.dumps(response)
    
#     except Exception as e:
#         return e
    
@app.route("/post/<requested_data>", methods=['POST'])
def post_data(requested_data):
    
    # there must be a better way of doing this
    if requested_data == "temp":
        collection = temp
    elif requested_data == "co2":
        collection = co2
    elif requested_data == "detections":
        collection = detections
    elif requested_data == "cameras":
        collection = cameras

    ins_data = request.get_json()
    
    try:
        try:
            data = collection.insert_many(ins_data)
            print("INSERT MANY")
        except:
            data = collection.insert_one(ins_data)
            print("INSERT ONE")
            
        print("inserting:")
        print(data)
        return str(data)
    
    except Exception as e:
        return json.dumps(e)
    
# @app.route("/post/detections", methods=['POST'])
# def post_detection():
#     ins_data = request.get_json()
    
#     try:
#         try:
#             data = detections.insert_many(ins_data)
#             print("INSERT MANY")
#         except:
#             data = detections.insert_one(ins_data)
#             print("INSERT ONE")
            
#         print("inserting:")
#         print(data)
#         return str(data)
    
#     except Exception as e:
#         return json.dumps(e)

# @app.route("/post/graphs/{graph_type}", methods=['POST'])
# def post_detection(graph_type):
    """
    Can we use a parameter to determine which graph ie temp/co2 to post the data to?
    """
#     ins_data = request.get_json()
    
#     try:
#         try:
#             data = detections.insert_many(ins_data)
#             print("INSERT MANY")
#         except:
#             data = detections.insert_one(ins_data)
#             print("INSERT ONE")
            
#         print("inserting:")
#         print(data)
#         return str(data)
    
#     except Exception as e:
#         return json.dumps(e)
        
app.run(debug=True, host='0.0.0.0', port=5000)