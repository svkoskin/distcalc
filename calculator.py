#!/usr/bin/env python2.7

import uuid

from flask import Flask, session, render_template, request

app = Flask(__name__)
app.debug = True
app.secret_key = "topsecret"

all_results = {}

def is_a_number(arg):
    try:
        float(arg)
    except ValueError:
        return False

    return True

def calculate(arg1_str, arg2_str, op):
    # Caller will catch ValueErrors raised by this
    arg1 = float(arg1_str)
    arg2 = float(arg2_str)

    if op == "+":
        return arg1 + arg2
    elif op == "-":
        return arg1 - arg2
    elif op == "*":
        return arg1 * arg2
    elif op == "/":
        return arg1 / arg2
    else:
        raise ValueError("Allowed operators are +, -, * and /")

@app.route("/")
def calculator_page():
    errors = []

    if "id" not in session:
        session["id"] = uuid.uuid4()

    if session["id"] not in all_results:
        all_results[session["id"]] = []

    curr_results = all_results[session["id"]]

    try: 
        arg1 = request.args["arg1"]
        arg2 = request.args["arg2"]
        op = request.args["op"]

        result = "{} {} {} = {}".format(
            arg1, op, arg2, calculate(arg1, arg2, op)
        )

        curr_results.append(result)

    except KeyError:
        # We didn't get arguments and that's fine. (for instance, on the first
        # page load this will happen)
        pass

    except ValueError as e:
        # We got some invalid values from the user who should be informed in 
        # returned page.
        errors.append(str(e))

    return render_template(
        "calculator.html", results=curr_results, errors=errors
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0")
