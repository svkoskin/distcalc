#!/usr/bin/env python2.7

import uuid

from flask import Flask, session, render_template, request

app = Flask(__name__)
app.debug = True
app.secret_key = "topsecret"

class Calculator(object):
    def __init__(self):
        self.all_results = {}

    def calculate(self, sess_id, arg1_str, arg2_str, op):
        if sess_id not in self.all_results:
            self.all_results[sess_id] = []

        curr_results = self.all_results[sess_id]

        # Caller will catch ValueErrors raised by this
        arg1 = float(arg1_str)
        arg2 = float(arg2_str)

        if op == "+":
            calc_result = arg1 + arg2
        elif op == "-":
            calc_result = arg1 - arg2
        elif op == "*":
            calc_result = arg1 * arg2
        elif op == "/":
            calc_result = arg1 / arg2
        else:
            raise ValueError("Allowed operators are +, -, * and /")

        result = "{} {} {} = {}".format(arg1, op, arg2, calc_result)

        curr_results.append(result)

    def get_results(self, sess_id):
        if sess_id not in self.all_results:
            self.all_results[sess_id] = []

        return self.all_results[sess_id]

calculator = Calculator()

@app.route("/")
def calculator_page():
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
        errors.append(str(e))

    return render_template(
        "calculator.html", results=calculator.get_results(session["id"]),
        errors=errors
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0")
