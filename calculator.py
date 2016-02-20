#!/usr/bin/env python2.7

import re
import StringIO
import uuid

from flask import Flask, jsonify, make_response, render_template, request, session
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
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

    def calculate_and_get_sin(self, expr):
        match_with_x = re.match(r"sin\(([\d.]+)x\)", expr)

        if match_with_x is not None:
            num = self._to_number(match_with_x.group(1))
            with_x = True
        else:
            match_with_constant = re.match(r"sin\(([\d.]+)\)", expr)

            if match_with_constant is not None:
                num = self._to_number(match_with_constant.group(1))
                with_x = False
            else:
                return "error"

        figure = Figure()

        axes = figure.add_subplot(1, 1, 1)
        xs = np.arange(-np.pi, np.pi, 0.01)

        if with_x:
            ys = [np.sin(num * x) for x in xs]
        else:
            ys = [np.sin(num) for x in xs]

        axes.plot(xs, ys)
        
        axes.set_xlabel("x")
        axes.set_ylabel(expr)
        axes.autoscale(tight=True)

        canvas = FigureCanvas(figure)
        output = StringIO.StringIO()
        canvas.print_png(output)
        return output.getvalue()

    def get_results(self, sess_id):
        if sess_id not in self.all_results:
            self.all_results[sess_id] = []

        return self.all_results[sess_id]

app = Flask(__name__)
app.debug = True
app.secret_key = "topsecret"

calculator = Calculator()

@app.route("/sin.png")
def get_sin():
    errors = []
    try:
        arg = request.args["arg"]
        sin_png = calculator.calculate_and_get_sin(arg)

        response = make_response(sin_png)
        response.mimetype = "image/png"
        return response

    except KeyError as e:
        errors.append(unicode(e))
        return errors
    except ValueError as e:
        errors.append(unicode(e))
        return errors

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
