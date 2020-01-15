import logging

from flask import request
from flask_restplus import Resource
from api.solver.business_logic import solve_sudoku
from api.restplus import api

log = logging.getLogger(__name__)

ns = api.namespace('solve', description='Operations related to solving sudokus')

@ns.route('/<string:state>')
class CategoryCollection(Resource):
    @api.response(201, 'Sudoku succesfully solved')
    def get(self, state):
        """
        Solves the sent Sudoku.
        """
        data = request.json
        print(state)
        solution = solve_sudoku(data)
        return solution

    @api.response(204, 'Category successfully updated.')
    def put(self, state):
        """
        Updates a blog category.

        Use this method to change the name of a blog category.

        * Send a JSON object with the new name in the request body.

        ```
        {
          "name": "New Category Name"
        }
        ```

        * Specify the ID of the category to modify in the request URL path.
        """
        data = request.json
        update_category(id, data)
        return None, 204
