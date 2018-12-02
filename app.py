from flask import Flask
from flask_restful import Resource, Api
from flask_restful.reqparse import RequestParser

import os, json
from os import listdir
from os.path import isfile, join

app = Flask(__name__)
api = Api(app, prefix="/api/v1")

subscriber_request_parser = RequestParser(bundle_errors=True)
subscriber_request_parser.add_argument("id", type=int, required=True, help="Please enter valid integer as ID")
subscriber_request_parser.add_argument("name", type=str, required=True, help="Name has to be valid string")
subscriber_request_parser.add_argument("command", type=str, required=True)


######################
# Auxiliary Function ###########################################################
######################
def filesInDir():
    # Returns a dictionary of files inside "services/" folder.
    res = [f for f in listdir('services/') if isfile(join('services/', f))]
    return res

def fileNamesInDir():
    # Returns a dictionary of filenames, without ".json" extension.
    res = []
    for f in listdir('services/'):
        if isfile(join('services/', f)):
            res.append(f[:-5])
    return res

def check_service_existence(s_name):
    res = fileNamesInDir()
    if s_name in res:
        return True
    else:
        return None

######################
# Main Program       ###########################################################
######################

class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

class ServiceCollection(Resource):
    def get(self):
        # a = os.listdir('/home/esb/03-proyectos/REST_APIs/python_REST_API/flask/flask_restful/esb_api/servicios')
        onlyfiles = filesInDir()

        res = {}
        res["services"] = []

        for p in onlyfiles:
            if p.endswith('.json'):
                data = {'name': p[:-5]}
                res["services"].append(data)
        return res

    def post(self):
        """
            {
             "id": 4,
             "name": "service4",
             "command": "Hello World Service 4!"
            }
        """
        onlyfiles = filesInDir() # List of files in 'services/' folder
        args = subscriber_request_parser.parse_args() # Arguments received in POST JSON

        filename = args['name'] + str('.json') # 'serviceX.json' format file.

        if filename not in onlyfiles:
            print("File Dir: " + str(filename))
            with open(os.path.join("services", filename), 'w') as f:
                json.dump(args, f)
                return {"msg": "Service added", "service_data": args}, 201

        else:
            return {"msg": "The specified service already exists."}, 422

class Service(Resource):
    def get(self, service_name):
        service = check_service_existence(service_name)
        if service:
            with open(os.path.join("services", service_name + str('.json'))) as f:
                data = json.load(f)
                return data
        else:
            return {"error": "Service not found."}, 404

    def put(self, service_name):
        args = subscriber_request_parser.parse_args()
        filename = service_name + str('.json') # 'serviceX.json' format file.
        if os.path.exists(os.path.join("services", service_name + str('.json'))):
            with open(os.path.join("services", filename), 'w') as f:
                json.dump(args, f)
                return {"msg": "Service updated", "service_data": args}
        else:
            return {"error": "Service not found."}, 404

    def delete(self, service_name):
        service = check_service_existence(service_name)
        # print("Service Name: " + str(service_name))
        # if service:
        if os.path.exists(os.path.join("services", service_name + str('.json'))):
            os.remove(os.path.join("services", service_name + str('.json')))
            return {"message": "Service deleted."}, 204
        else:
            return {"error": "Service not found"}, 404

api.add_resource(HelloWorld, '/')
api.add_resource(ServiceCollection, '/services')
api.add_resource(Service, '/services/<service_name>')

if __name__ == '__main__':
    app.run(debug=True)
