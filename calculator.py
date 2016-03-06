#!/usr/bin/env python2.7

import re
import uuid

from flask import Flask, jsonify, render_template, request, session
import numpy as np


class Calculator(object):
    def __init__(self):
        self.all_results = {}

    @staticmethod
    def _to_number(number_str):
        try:        
            return int(number_str)
        except ValueError:
            try:
                return float(number_str)
            except ValueError as e:
                raise e

    def calculate(self, sess_id, arg1_str, arg2_str, op):
        if sess_id not in self.all_results:
            self.all_results[sess_id] = []

        curr_results = self.all_results[sess_id]

        # Caller will catch ValueErrors raised by this
        arg1 = self._to_number(arg1_str)
        arg2 = self._to_number(arg2_str)

        if op == "+":
            calc_result = arg1 + arg2
        elif op == "-":
            calc_result = arg1 - arg2
        elif op == "*":
            calc_result = arg1 * arg2
        elif op == "/":
            calc_result = float(arg1) / float(arg2)
        else:
            raise ValueError("Allowed operators are +, -, * and /")

        result = "{} {} {} = {}".format(arg1, op, arg2, calc_result)

        curr_results.append(result)

        return calc_result

    def calculate_and_get_sin(self, coef):
        num = float(coef)

        xs = np.arange(-np.pi, np.pi, 0.01)
        return [(x, np.sin(num * x)) for x in xs]

    def get_results(self, sess_id):
        if sess_id not in self.all_results:
            self.all_results[sess_id] = []

        return self.all_results[sess_id]

app = Flask(__name__)
app.debug = True
app.secret_key = "topsecret"

calculator = Calculator()

@app.route("/sin.json")
def get_sin():
    errors = []
    try:
        coef = request.args["coef"]
        sin_vals = calculator.calculate_and_get_sin(coef)

        return jsonify(sinValues=sin_vals, errors=errors)

    except KeyError as e:
        errors.append(unicode(e))
        return jsonify(errors=errors)
    except ValueError as e:
        errors.append(unicode(e))
        return jsonify(errors=errors)

@app.route("/calculations.json")
def get_calculations_ajax():
    if "id" not in session:
        session["id"] = unicode(uuid.uuid4())

    return jsonify(results=calculator.get_results(session["id"]))

@app.route("/do_calculation.json")
def do_calculate_ajax():
    errors = []    

    if "id" not in session:
        session["id"] = unicode(uuid.uuid4())

    try: 
        arg1 = request.args["arg1"]
        arg2 = request.args["arg2"]
        op = request.args["op"]

        calc_result = calculator.calculate(session["id"], arg1, arg2, op)

    except KeyError as e:
        errors.append(unicode(e))

    except ValueError as e:
        # We got some invalid values from the user who should be informed in 
        # returned page.
        errors.append(unicode(e))

    return jsonify(calcResult=calc_result, errors=errors)

@app.route("/")
def calculator_page():
    return render_template("calculator.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0")
