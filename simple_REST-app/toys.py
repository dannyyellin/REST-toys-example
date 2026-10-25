# This is example REST API server code for lecture: topic-2 REST APIs
# It uses Flask to build a RESTful service in Python.
# A good introduction is https://towardsdatascience.com/the-right-way-to-build-an-api-with-python-cd08ab285f8f
# See also https://dzone.com/articles/creating-rest-services-with-flask
# To run this program, in terminal window issue the cmd:
#   python3 toys.py
# Alternatively, comment out "app.run..." cmd in __main__ and issue the following cmds
#   export FLASK_APP-"toys.py"
#   flask run --port 8001     (or whatever port you want to run on.  if no "--port" option specified, it is port 5000)
# flask will return the IP and port the app is running on
# you must install the packages Flask before running this program
# To run in docker container, can use Dockerfile in this directory.   Issue the commands
#   docker build --tag toys .
#   docker run -p8001:8001 toys
# The frst cmd builds the toys docker image.   It sets the port the app is listening on to be 8001. (See Dockerfile).
# The second cmd runs the image created in the previous cmd. The -p option indicates that requests issues to port 8001
# will get forwarded to the port 8001 of the Docker container.
# Test application either (1) POSTMAN, (2) curl, or (3) write a  program to test

# The resources are:
# /toys          This is a collection resource
# /toys/{id}     This is the toy given by the identifier id.  id is a UUID represented as a string.
# A toy is of the form:
# {
#     'id': 'string',
#     'name':'string',
#     'descr': 'string',
#     'age': integer,
#     'price': 'float',
#     'features': 'array'
# }
# age is the minimal child age fit for this toy.
# 'features' is an array of strings, where each string describes a different feature of the toy.
# See https://json-schema.org/learn/getting-started-step-by-step on how to define JSON schema

from flask import Flask, jsonify, request, make_response
import sys

global N
N = 0

def genID():
    global N
    N += 1
    return(str(N))


app = Flask(__name__)  # initialize Flask
Toys = {}


@app.route('/toys', methods=['POST'])
def addToy():
    print("POST toys")
    try:
        content_type = request.headers.get('Content-Type')
        if content_type != 'application/json':
            return jsonify("{error: Expected application/json}"), 415  # 415 Unsupported Media Type
        data = request.get_json()
        # Check if required fields are present
        required_fields = ['name', 'age', 'price']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Malformed data"}), 400
        newID = genID()      # returns string ID
        if 'features' not in data:
            features = []
        else:
            features = data['features']
        if 'descr' not in data:
            descr = "Not Available"
        else:
            descr = data['descr']
        toy = {
            "id":newID,
            "name":data["name"],
            "descr":descr,
            "age":int(data["age"]),
            "price":data["price"],
            "features":features
        }
        Toys[newID] = toy
        return toy, 201
        # return jsonify(toy),201
    except Exception as e:
        print("Exception: ", str(e))
        return jsonify({"server error":str(e)}),500

@app.route('/toys', methods=['GET'])
def getToys():
    try:
        # query strings (qs) must be of the form x=a or conjunctions x=a&y=b&z=c etc.
        query_params = request.args.to_dict()
        print("query_parms=", query_params)
        if not query_params:
            return list(Toys.values()), 200
        else:
            # if query string if of the form x=a&y=b then query_parms is {x:a,y:b}
            print("query_params = ", query_params)
            results = [
                item for item in Toys.values()
                if all((str(item.get(k)) == v) for k, v in query_params.items())
            ]
            print("results = ",results)
            sys.stdout.flush()
            return jsonify(list(results))
            # return list(Toys.values()), 200
    except Exception as e:
        print("Exception: ", str(e))
        return jsonify({"server error":str(e)}),500


@app.route('/toys/<string:toyid>', methods=['GET'])
def getToy(toyid):
    print("GET toys")
    try:
        toy = Toys[toyid]
    except KeyError:
        print("GET request error: No such ID")
        return jsonify({"error":"Not found"}), 404
    except Exception as e:
        print("Exception: ", str(e))
        return jsonify({"server error":str(e)}),500
    return jsonify(toy), 200



@app.route('/toys/<string:toyid>', methods=['DELETE'])
def delToy(toyid):
    print("DELETE toys")
    try:
        del Toys[toyid]
        return '', 204
    except KeyError:
        print("GET request error: No such ID")
        return jsonify({"error":"Not found"}), 404
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
        if not Toys[toyid]:
            print("PUT error:No such ID")
            # no toy of this id exists
            return jsonify({"error":"Not found"}), 404
        toy = {
            'id': toyid,
            'name':data['name'],
            'descr': descr,
            "age": data["age"],
            'price': data['price'],
            'features': features
        }
        Toys[toyid] = toy
        return toy
    except Exception as e:
        print("Exception: ", str(e))
        return jsonify({"server error":str(e)}),500
        # response_data = {"id": toyid}
        # return jsonify(response_data), 200

if __name__ == '__main__':
    print("running toys server")
    # run Flask app.   default part is 5000
    app.run(host='0.0.0.0', port=8001, debug=True)
