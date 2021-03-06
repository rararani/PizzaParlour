from flask import Flask, request, jsonify
from order import Order
from order_builder import OrderBuilder
from jsonwrite import get_order_ids, write_to_json, remove_from_json, convert_to_csv, get_order
from reader import get_reader, get_prices
import jsonwrite
import json
import csv

app = Flask("Assignment 2")

@app.route('/pizza')
def welcome_pizza():
    return "Welcome to Pizza Parlour!"


@app.route('/create', methods=['POST'])
def create_order() -> str:
    '''
    Uploads the new order into the respective data files. If delivery method is foodora, will upload it to orders.csv,
    if delivery method is ubereats or in-house, uploads the order to orders.csv
    '''
    builder = OrderBuilder()

    builder.build_orderid()
    builder.build_drink(request.json['_drink'])
    builder.build_size(request.json['_size'])
    builder.build_toppings(request.json['_extra_toppings'])
    builder.build_type(request.json['_type'])
    builder.build_price(get_prices())

    new_order = builder.build()

    write_to_json(new_order)

    order_info = {"_order_id": new_order.get_order_id()}
    order_info["_status"] = 201

    response = app.response_class(response=json.dumps(order_info), status=201, mimetype='application/json')

    return response


@app.route("/update", methods=['POST'])
def update_order() -> str:
    '''
    Updates a prexisting order in orders.csv or orders.json depending on the delivery type: foodora or, ubereats/in-house respectively.

    Precondition: user inputs their previous order_id, and all other fields that may or may not be changed
    '''

    keys = get_order_ids()

    order_id = request.json['_order_id']
    order_info = {"_order_id": order_id}


    if order_id not in keys:
        order_info["_status"] = 404

        response = app.response_class(response=json.dumps(order_info), status=404, mimetype='application/json')
    else:
        builder = OrderBuilder()

        builder.build_update_orderid(order_id)
        builder.build_drink(request.json['_drink'])
        builder.build_size(request.json['_size'])
        builder.build_toppings(request.json['_extra_toppings'])
        builder.build_type(request.json['_type'])
        builder.build_price(get_prices())

        new_order = builder.build()

        write_to_json(new_order)

        order_info["_status"] = 201

        response = app.response_class(response=json.dumps(order_info), status=201, mimetype='application/json')

    return response


@app.route("/cancel", methods=['POST'])
def cancel_order() -> str:
    '''
    Cancels a prexisting order in orders.json depending on the delivery type: foodora or, ubereats/in-house respectively.

    Precondition: order_id is prexisting in the appropriate delivery type
    '''
    keys = get_order_ids()
    order_info = {"_order_id": request.json["_order_id"]}
    order_id = request.json['_order_id']


    if order_id not in keys:
        order_info["_status"] = 404
        
        response = app.response_class(response=json.dumps(order_info), status=404, mimetype='application/json')
    else:
        remove_from_json(order_id)

        order_info["_status"] = 200
        
        response = app.response_class(response=json.dumps(order_info), status=200, mimetype='application/json')

    return response

@app.route("/deliver", methods=['GET'])
def request_delivery():
    '''
    Requests delivery of the pizza.

    Precondition: Input should look like:

    {
        "_delivery": "foodora",
        "_order_id": "34324217871822",
        "_address": "123 depression street",
    } 
    '''
    keys = get_order_ids()
    order_info = {"_order_id": request.json["_order_id"]}
    order_id = request.json['_order_id']

    if order_id not in keys:
        order_info["_status"] = 404

        response = app.response_class(response=json.dumps(order_info), status=404, mimetype='application/json')
    else:
        if request.json["_delivery"] == "foodora":
            order = convert_to_csv(order_id)    
        else:
            order = get_order(order_id)
        
        order_info["_status"] = 200
        order_info["_order"] = order
        order_info["_address"] = request.json["_address"]
        order_info["_delivery"] = request.json["_delivery"]

        response = app.response_class(response=json.dumps(order_info), status=200, mimetype='application/json')

    return response

@app.route("/menu", methods=['GET'])
def get_menu():
    '''
    Returns the list of lines from the menu
    '''
    return jsonify(get_reader())


@app.route("/price", methods=['GET'])
def request_menu_prices():
    '''
    Returns a JSON with all the prices in the menu.
    '''
    items_dict = get_prices()

    response = app.response_class(response=json.dumps(items_dict), status=200, mimetype='application/json')

    return response


if __name__ == "__main__":
    app.run()
