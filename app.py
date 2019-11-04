from pprint import pprint

from dotenv import load_dotenv, find_dotenv
from flask import Flask, render_template, session, request, json, jsonify
from markupsafe import Markup
import os

from game import Game


app = Flask(__name__)
load_dotenv(find_dotenv(usecwd=True))
app.config.from_object('config_default')
app.config.from_envvar('APPLICATION_SETTINGS')


@app.route('/', methods=['GET'])
def start():

    Game.start_up(seed=app.config.get('SEED', None))
    game = Game(debug=app.config.get('DEBUG', False))
    status = game.hunter.start_up(game.hazards)
    session['game'] = game.to_json()

    cave_id = game.hunter.cave.id
    game.hunter.notebook.consult_notebook(cave_id)

    cavern_map = None
    with open(os.path.join(f"notes/notebook_{cave_id}.gv.svg"), 'r') as svg_file:
        cavern_map = Markup(svg_file.read())

    #pprint(status)

    return render_template("game_board.html", game=game, status=status, cavern_map=cavern_map)


@app.route('/play', methods=['POST'])
def play():
    game = Game.from_json(session['game'])
    status = []
    errors = []

    action = json.loads(request.data).get('play', None)
    cave_id = json.loads(request.data).get('cave_id', None)
    action = action.strip()[0].lower() if action else None
    cave_id = int(cave_id) if cave_id else None

    if action not in ['m', 's']:
        errors.append("You must either enter or shoot into an adjoining cave.")
    if cave_id not in range(1, 21):
        errors.append("You must select a valid cave id.")

    if not errors:
        if action == 'm':
            status, errors = game.hunter.move(game.hazards, cave_id)
        else:
            status, errors = game.hunter.shoot(game.wumpus, cave_id, game.hazards)
        session['game'] = game.to_json()

    if errors:
        return jsonify({"errors": errors}), 400

    game.hunter.notebook.consult_notebook(cave_id)

    cavern_map = None
    with open(os.path.join(f"notes/notebook_{cave_id}.gv.svg"),'r') as svg_file:
        cavern_map = svg_file.read()

    status_json = [{"type": status_message.type, "source": status_message.source, "content": status_message.content}
                   for status_message in status]

    return jsonify({"status": status_json,
                    "cave_ids": game.hunter.cave.neighboring_caves,
                    "arrows": game.hunter.quiver,
                    "game_over": not(game.wumpus.alive and game.hunter.alive),
                    "notes": cavern_map}), 200


app.run()
