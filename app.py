import json

import flask
import os
import pathlib
from flask import Flask
from flask import request, jsonify
from utils import ExclusionGroup, Individual, connections_list_to_dict, connections_list_from_dict
from solvers import NetworkXAssignmentSolver
from notifiers import TwilioNotifier
from loguru import logger


app = Flask(__name__)


@app.route('/solve', methods=['POST'])
def solve():
    request_json = request.get_json()
    try:
        request_data = request_json["data"]
        groups = [ExclusionGroup.from_dict(grp) for grp in request_data["groups"]]
        individuals = request_data["individuals"]
        solver = NetworkXAssignmentSolver([
            Individual.from_dict(idv, groups_list=groups) for idv in individuals
        ])
        connections = solver.solve()
        response_data = connections_list_to_dict(connections)
        return jsonify(isError=False,
                       message="OK",
                       statusCode=200,
                       data=response_data), 200
    except KeyError as e:
        logger.error(f"Malformed key: {e}")
        return jsonify(isError=True,
                       message="Malformed key",
                       statusCode=500), 500
    except IndexError as e:
        logger.error(f"Invalid index: {e}")
        return jsonify(isError=True,
                       message="Invalid group index",
                       statusCode=500), 500
    except RuntimeError as e:
        logger.error(f"Unable to solve problem: {e}")
        return jsonify(isError=True,
                       message=f"Unable to solve problem. Make sure too many people don't belong to the same group!",
                       statusCode=500), 500


@app.route('/notify', methods=['POST'])
def notify():
    request_json = request.get_json()
    errors = []
    try:
        request_data = request_json["data"]
        connections = connections_list_from_dict(request_data)
        notifier = TwilioNotifier(
            os.environ["TWILIO_MESSAGING_SERVICE_SID"],
            os.environ["TWILIO_ACCOUNT_SID"],
            os.environ["TWILIO_AUTH_TOKEN"])
        for sender, recipient in connections:
            try:
                notifier.notify(sender, recipient)
            except RuntimeError as re:
                logger.error(f"Unable to send message to {sender.contact} ({sender.name}): {re}")
                errors.append(f"Unable to send message to {sender.contact} ({sender.name})")
        if len(errors) > 0:
            raise RuntimeError("Detected errors when sending messages")
        return jsonify(isError=False,
                       message="OK",
                       statusCode=200), 200
    except KeyError as e:
        logger.error(f"Malformed key: {e}")
        return jsonify(isError=True,
                       message="Malformed key",
                       statusCode=500), 500
    except IndexError as e:
        logger.error(f"Invalid index: {e}")
        return jsonify(isError=True,
                       message="Invalid group index",
                       statusCode=500), 500
    except RuntimeError as e:
        logger.error(f"{', '.join(errors)}: {e}")
        return jsonify(isError=True,
                       message=", ".join(errors),
                       statusCode=500), 500


if __name__ == '__main__':
    app.run()
