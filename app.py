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

    debug = app.config.get('DEBUG', False)
    Game.start_up(seed=app.config.get('SEED', None))
    game = Game()
    status = game.hunter.start_up(game.hazards)
    if debug:
        game.display_configuration()
        print(game.hunter)

    session['game'] = game.to_json()

    cave_id = game.hunter.cave.id
    game.hunter.notebook.consult_notebook(cave_id)

    cavern_map = None
    with open(os.path.join(f"notes/notebook_{cave_id}.gv.svg"), 'r') as svg_file:
        cavern_map = Markup(svg_file.read())

    #pprint(status)

    return render_template("game_board.html", game=game, status=status, cavern_map=cavern_map)


@app.route('/move', methods=['POST'])
def move():

    debug = app.config.get('DEBUG', False)
    game = Game.from_json(session['game'])
    status = []
    errors = []

    cave_id = json.loads(request.data).get('cave_id', None)
    move = json.loads(request.data).get('move', None)
    move = move.strip()[0].lower() if move else None
    cave_id = int(cave_id) if cave_id else None

    if move not in ['e', 's']:
        errors.append("You must either enter or shoot into an adjoining cave.")
    if cave_id not in range(1, 21):
        errors.append("You must select a valid cave id.")

    if not errors:
        if debug and not game.wumpus.asleep:
            print(game.wumpus)
        if move == 'e':
            status, errors = game.hunter.enter(cave_id, game.hazards)
        else:
            status, errors = game.hunter.shoot(cave_id, game.hazards)
        session['game'] = game.to_json()

    if errors:
        return jsonify({"errors": errors}), 400

    # Note that the relevant cave id for the notebook is the cave in which the hunter is located and not the
    # cave the hunter shoots into (in the event that the hunter took a shot).
    game.hunter.notebook.consult_notebook(game.hunter.cave.id)

    cavern_map = None
    with open(os.path.join(f"notes/notebook_{game.hunter.cave.id}.gv.svg"),'r') as svg_file:
        cavern_map = svg_file.read()

    status_json = [{"type": status_message.type, "source": status_message.source, "content": status_message.content}
                   for status_message in status]

    return jsonify({"status": status_json,
                    "cave_ids": game.hunter.cave.neighboring_caves,
                    "arrows": game.hunter.quiver,
                    "game_over": not(game.wumpus.alive and game.hunter.alive),
                    "notes": cavern_map}), 200


app.run()
