import logging
import json

import numpy as np
import collections
from flask import request, jsonify
from flask_restplus import Resource
from api.solver.business_logic import solve_sudoku
from api.restplus import api

log = logging.getLogger(__name__)
ns = api.namespace('solve', description='Operations related to solving sudokus')

size = 9
square_size = 3

def return_result(status="success", code=200, message="", data=None):
    return jsonify(status=status, code=code, message=message, data=data)

def flat_array_to_rows(sudoku_state):
    rows = []
    for i in range(size):
        row_to_add = []
        for j in range(size):
            row_to_add.append(sudoku_state[i*size+j])
        rows.append(row_to_add)
    return rows

def init_state_from_rows(rows):
    state = []
    row_number = 1
    for row in rows:
        add_row(state, row, row_number)
        row_number += 1
    return state

def add_row(state, row, row_number):
    column = 1
    for value in row:
        if value == 0:
            meta_sq = np.floor((row_number-1)/square_size)*square_size+np.floor((column-1)/square_size)+1
            box = {'column_number': column, 'row_number': row_number, 'square_number': int(meta_sq), 'value': 0, 'possible_values': [i+1 for i in range(size)]}
            state.append(box)
            column += 1
        if value != 0:
            meta_sq = np.floor((row_number-1)/square_size)*square_size+np.floor((column-1)/square_size)+1
            box = {'column_number': column, 'row_number': row_number, 'square_number': int(meta_sq), 'value': value, 'possible_values': []}
            state.append(box)
            column += 1
    return state

def print_current_state(state):
    col = 1
    row_print = []
    for box in state:
        row_print.append(box['value'])
        col += 1
        if col == size+1:
            print(row_print)
            col = 1
            row_print = []
    return None

def state_to_flat_string(state):
    flat_state = []
    for box in state:
        flat_state.append(box['value'])
    return flat_state

def fill_in_squares_with_one_possible_value(state):
    for box in state:
        if (box['value'] == 0):
            if len(box['possible_values']) < 1:
                print('error in possible_values')
            if len(box['possible_values']) == 1:
                box['value'] = possible_values[0]
                is_mutated = True
    return state

def eliminate_column_row_square_possibilities(state):
    new_state = state
    for prime_box in state:
        if prime_box['value'] != 0:
            for search_box in new_state:
                if (search_box['value'] == 0):
                    if (prime_box['column_number'] == search_box['column_number']):
                        try:
                            search_box['possible_values'].remove(prime_box['value'])
                            is_mutated = True
                        except:
                            pass
                    if (prime_box['row_number'] == search_box['row_number']):
                        try:
                            search_box['possible_values'].remove(prime_box['value'])
                            is_mutated = True
                        except:
                            pass
                    if (prime_box['square_number'] == search_box['square_number']):
                        try:
                            search_box['possible_values'].remove(prime_box['value'])
                            is_mutated = True
                        except:
                            pass
    return new_state

def is_different_box(prime_box, option_box):
    answer = True
    if (prime_box['column_number'] == option_box['column_number']):
        if (prime_box['row_number'] == option_box['row_number']):
            if (prime_box['square_number'] == option_box['square_number']):
                answer = False
    return answer

def check_square_uniqueness(state):
    for prime_box in state:
        if prime_box['value'] == 0:
            for possibility in prime_box['possible_values']:
                square_count = 0
                for search_box in state:
                    if search_box['value'] == 0:
                        if (prime_box['square_number'] == search_box['square_number'] and is_different_box(prime_box, search_box)):
                            if (possibility in search_box['possible_values']):
                                square_count += 1
                if (square_count == 0):
                    prime_box['value'] = possibility
                    prime_box['possible_values'] = []
    return state

def check_row_uniqueness(state):
    for prime_box in state:
        if prime_box['value'] == 0:
            for possibility in prime_box['possible_values']:
                row_count = 0
                for search_box in state:
                    if search_box['value'] == 0:
                        if (prime_box['row_number'] == search_box['row_number'] and is_different_box(prime_box, search_box)):
                            if (possibility in search_box['possible_values']):
                                row_count += 1
                if (row_count == 0):
                    prime_box['value'] = possibility
                    prime_box['possible_values'] = []
    return state

def check_column_uniqueness(state):
    for prime_box in state:
        if prime_box['value'] == 0:
            for possibility in prime_box['possible_values']:
                column_count = 0
                for search_box in state:
                    if search_box['value'] == 0:
                        if (prime_box['column_number'] == search_box['column_number'] and is_different_box(prime_box, search_box)):
                            if (possibility in search_box['possible_values']):
                                column_count += 1
                if (column_count == 0):
                    prime_box['value'] = possibility
                    prime_box['possible_values'] = []
    return state

def check_valid_and_solved_sudoku(state):
    solved_one = True
    for box in state:
        if box['value'] == 0:
            solved_one = False

    solved_two = True
    good_result = [i+1 for i in range(size)]

    for column_number in good_result:
        result = []
        for box in state:
            if box['column_number'] == column_number:
                result.append(box['value'])
        if (collections.Counter(result) != collections.Counter(good_result)):
            solved_two = False

    for row_number in good_result:
        result = []
        for box in state:
            if box['row_number'] == row_number:
                result.append(box['value'])
        if (collections.Counter(result) != collections.Counter(good_result)):
            solved_two = False

    for square_number in good_result:
        result = []
        for box in state:
            if box['square_number'] == square_number:
                result.append(box['value'])
        if (collections.Counter(result) != collections.Counter(good_result)):
            solved_two = False

    return (solved_one and solved_two)


def check_column_row_square_uniqueness(state):
    state = check_row_uniqueness(state)
    state = eliminate_column_row_square_possibilities(state)
    state = check_column_uniqueness(state)
    state = eliminate_column_row_square_possibilities(state)
    state = check_square_uniqueness(state)
    state = eliminate_column_row_square_possibilities(state)
    return state

def solve_sudoku(request_sudoku):
    state = flat_array_to_rows(request_sudoku)
    state = init_state_from_rows(state)
    for i in range(100):
        state = eliminate_column_row_square_possibilities(state)
        state = check_column_row_square_uniqueness(state)
    return state_to_flat_string(state)

# size = 16
# state = initialize()
#
# for i in range(100):
#     state = eliminate_column_row_square_possibilities(state)
#     state = check_column_row_square_uniqueness(state)
#
# print_current_state(state)
# print('solved: ' + str(check_valid_and_solved_sudoku(state)))

@ns.route('/')
class CategoryCollection(Resource):
    @api.response(201, 'successfully posted')
    def post(self):
        data = request.data
        requestData = json.loads(data.decode("utf-8"))
        print(requestData['sudokuState'])
        response_data = {}
        response_data['sudokuSolution'] = solve_sudoku(requestData['sudokuState'])
        return return_result(data=response_data)
