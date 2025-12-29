# this is same as WebServer/toys-robust.py except for port
import sys

from flask import Flask, jsonify, request
import pymongo
from bson import ObjectId
import os


app = Flask(__name__)  # initialize Flask
client = pymongo.MongoClient('mongodb://mongo:27017/')
db = client['toys_inventory']
toysColl = db['toys']


@app.route('/toys', methods=['POST'])
def addToy():
    print("POST toys")
    sys.stdout.flush()
    try:
        content_type = request.headers.get('Content-Type')
        if content_type != 'application/json':
            return jsonify("{error: Expected application/json}"), 415  # 415 Unsupported Media Type
        data = request.get_json()
        # Check if required fields are present
        required_fields = ['name', 'age', 'price']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Malformed data"}), 400
        if 'features' not in data:
            features = []
        else:
            features = data['features']
        if 'descr' not in data:
            descr = "Not Available"
        else:
            descr = data['descr']
        toy = {
            'name':data['name'],
            'descr':descr,
            'age':data['age'],
            'price':data['price'],
            'features':features
        }
        print('inserting toy = ', toy)
        result = toysColl.insert_one(toy)
        id = str(result.inserted_id)
        # NOTE that we are only returning the JSON containing the id of the toys, not the entire toy object
        response_data = {"id":id}
        return jsonify(response_data),201
    except Exception as e:
        print("Exception: ", str(e))
        return jsonify({"server error":str(e)}),500


@app.route('/toys', methods=['GET'])
def getToys():
    print("GET ALL request")
    sys.stdout.flush()
    try:
        # say query string is of form "?x=y&a=b".   Then request.args is a MultiDict.   You can get the values by the
        # instructions:   value_a=request.args.get('a') and value_b=request.args.get('b').  (It is a MultiDict and not
        # a Dict because you can have a query string of the form "?x=y&x=b".
        query_params = request.args.to_dict()
        # type of query params is  <class 'dict'>
        if query_params:  # query params is not empty
            if 'id' in query_params:
                # convert the string into a mongoDB ID
                print('query_params1 = ', query_params)
                query_params['_id'] = ObjectId(query_params["id"])
                del query_params["id"]
            if 'price' in query_params:
                # convert the string into a float
                query_params['price'] = float(query_params['price'])
            if 'age' in query_params:
                # convert the string into an int
                    query_params['age'] = int(query_params['age'])
        toys = toysColl.find(query_params)
        # type of toys is <class 'pymongo.synchronous.cursor.Cursor'>
        list_of_toy = list(toys)
        # type of list_of_toy is list of objects
        # need to turn list_of_toy into a list of objects that do not contain ObjectIds
        return_toys = []
        for toy in list_of_toy:
            toy['id'] = str(toy['_id'])
            del toy['_id']
            return_toys.append(toy)
        response = jsonify(return_toys)
        response.headers.add('Access-Control-Allow-Origin', '*')
        # added the following to try to fix problem.   Not sure if needed.
        response.headers.add('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept')
        return response, 200
    except Exception as e:
        print("Exception: ", str(e))
        return jsonify({"server error": str(e)}), 500


@app.route('/toys/<string:toyid>', methods=['GET'])
def getToy(toyid):
    print("GET toys")
    sys.stdout.flush()
    try:
        # print("stockid = ", stockid)
        record = toysColl.find_one({"_id": ObjectId(toyid)})
        if record:
            # print("found stock with that id")
            toy = {}
            for field in record:
                if field == "_id":
                    toy['id'] = str(record["_id"])
                else:
                    toy[field] = record[field]
            return jsonify(toy), 200  # dict, need to turn into json before returning
        else:
            print("GET request error: No such ID")
            return jsonify({"error": "Not found"}), 404
    except Exception as e:
        print("Exception: ", str(e))
        return jsonify({"server error":str(e)}),500


@app.route('/toys/<string:toyid>', methods=['DELETE'])
def delToy(toyid):
    print("DELETE toys")
    sys.stdout.flush()
    try:
        result = toysColl.delete_one({"_id": ObjectId(toyid)})
        if result.deleted_count > 0:
            return 'foo', 204
        else:
            return jsonify({"error": "Not found"}), 404
        return '', 204
    except Exception as e:
        print("Exception: ", str(e))
        return jsonify({"server error":str(e)}),500


@app.route('/toys/<string:toyid>', methods=['PUT'])
def update(toyid):
    print("PUT toys")
    try:
        content_type = request.headers.get('Content-Type')
        if content_type != 'application/json':
            return jsonify({"error":"Expected application/json media type"}), 415  # 415 Unsupported Media Type
        data = request.get_json()
        # Check if required fields are present
        required_fields = ['name','age','price']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Malformed data"}), 400
        if 'features' not in data:
            features = []
        else:
            features = data['features']
        if 'descr' not in data:
            descr = "No description Available"
        else:
            descr = data['descr']
        toy = {
            'id': ObjectId(toyid),
            'name':data['name'],
            'descr': descr,
            "age": data["age"],
            'price': data['price'],
            'features': features
        }
        result = toysColl.find_one_and_update(
            {"_id": ObjectId(toyid)},
            {"$set": data},
            return_document=pymongo.ReturnDocument.AFTER
        )
        if result.keys():
            resp = {'id': str(result["_id"])}
            return jsonify(resp), 200
        else:
            return jsonify({"error": "Not found"}), 404
        response_data = {"id": toyid}
        return jsonify(response_data), 200
    except Exception as e:
        print("Exception: ", str(e))
        return jsonify({"server error":str(e)}),500

@app.route('/kill', methods=['GET'])
def kill_container():
    # x = 5/0   exception is caught by flask and it handled does not work.
    # sys.exit(1)  this also did now work
    os._exit(1)   # this works!@



if __name__ == '__main__':
    print("running toys server")
    app.run(host='0.0.0.0', port=80, debug=True)
