import os
import sys
from turtle import title
from typing import NewType
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO DONE implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_all_drinks():

    all_drinks = Drink.query.all()

    # if len(all_drinks) == 0:
    #     abort(404)

    return jsonify({
        'success': True,
        'drinks': [d.short() for d in all_drinks]
    })

'''
@TODO DONE implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drink_detail(payload):
    all_drinks = Drink.query.all()

    if len(all_drinks) == 0:
        abort(404)

    return jsonify({
        'success': True,
        'drinks': [d.long() for d in all_drinks]
    })

'''
@TODO DONE implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_new_drink(payload):

    body = request.get_json()
    try:
        new_title = body['title']
        new_recipe = body['recipe']

        fresh_drink = Drink(
            title=new_title,
            recipe=json.dumps(new_recipe)
        )
        fresh_drink.insert()

        return jsonify({
            'success': True,
            'drinks': [fresh_drink.long()]
        })
    except:
        print(sys.exc_info())
        abort(422)

'''
@TODO DONE implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_update_drink(payload, drink_id):

    body = request.get_json()
    drink_to_edit = Drink.query.filter(Drink.id == drink_id).one_or_none()

    if drink_to_edit is None:
        abort(404)

    try:
        drink_to_edit.title = body['title']
        drink_to_edit.recipe = json.dumps(body['recipe'])

        drink_to_edit.update()

        return jsonify({
            'success': True,
            'drinks': [drink_to_edit.long()]
        })
    except:
        abort(422)



'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):

    drink_to_delete = Drink.query.filter(Drink.id == id)

    if drink_to_delete is None:
        abort(404)
    
    try:
        drink_to_delete.delete()

        return jsonify({
            'success': True,
            'delete': drink_to_delete.id
        })

    except:
        abort(422)


# Error Handling
'''
Example error handling for unprocessable entity
'''
'''
@TODO DONE implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Unprocessable request"
    }), 422

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'Resource not found'
    }), 404

@app.errorhandler(405)
def not_allowed(error):
    return jsonify({
        'success': False,
        'error': 405,
        'message': 'Operation not allowed'
    }), 405

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'Bad request detected'
    }), 400


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error
    }), 401