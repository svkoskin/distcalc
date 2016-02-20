#!/usr/bin/env python2.7

import uuid

from flask import Flask, jsonify, render_template, request, session

app = Flask(__name__)
app.debug = True
app.secret_key = "topsecret"

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

    def get_results(self, sess_id):
        if sess_id not in self.all_results:
            self.all_results[sess_id] = []

        return self.all_results[sess_id]

calculator = Calculator()

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

        calculator.calculate(session["id"], arg1, arg2, op)

    except KeyError:
        # We didn't get arguments and that's fine. (for instance, on the first
        # page load this will happen)
        print "Got KeyError"

    except ValueError as e:
        # We got some invalid values from the user who should be informed in 
        # returned page.
        errors.append(unicode(e))

    return jsonify(errors=errors)

@app.route("/")
def calculator_page():
    return render_template(
        "calculator.html"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0")
