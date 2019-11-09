from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv, find_dotenv
from flask import Flask, render_template, session, request, json, jsonify
from markupsafe import Markup
import os
import logging

from game import Game

logger = logging.getLogger("")

app = Flask(__name__)
load_dotenv(find_dotenv(usecwd=True))
app.config.from_object('config_default')
app.config.from_envvar('APPLICATION_SETTINGS')

# Format for file logging.
formatter = logging.Formatter('%(asctime)s \t%(levelname)s\t%(module)s\t%(process)d\t%(thread)d\t%(message)s')


# File logger - rotates for every 1Mb up to 5 files.
file_handler = RotatingFileHandler(os.environ.get("LOG_FILE", 'logs/wumpus.log'), maxBytes=1_000_000, backupCount=5)
file_handler.setLevel(os.environ.get('LOG_LEVEL', logging.WARN))
file_handler.setFormatter(formatter)
logger.setLevel(os.environ.get('LOG_LEVEL', logging.WARN))
logger.addHandler(file_handler)


@app.route('/', methods=['GET'])
def start():
    """
    Sets up the game initially and returns a game board along with those initial conditions.
    :return: web page containing a game board
    """

    debug = app.config.get('DEBUG', False)
    Game.start_up(seed=app.config.get('SEED', None))
    game = Game()
    status = game.hunter.start_up(game.hazards)
    if debug:
        game.display_configuration()
        logger.debug(game.hunter)

    # Sadly, flask makes use of client-side sessions in the form of a session cookie.  So the state of the game must be
    # json serializable and small enough to be accommodated in a cookie.
    session['game'] = game.to_json()

    cave_id = game.hunter.cave.id
    cavern_map = game.hunter.notebook.consult_notebook(cave_id)

    return render_template("game_board.html", game=game, status=status, cavern_map=Markup(cavern_map))


@app.route('/turn', methods=['POST'])
def turn():
    """
    Response to an ajax request containing the hunter's turn selections (enter or shoot and cave id).  The only error
    possible if the browser is used properly, is the omission of a cave id selection.
    :return: json containing game status messages, arrows remaining, whether the game is over (won or lost), and
    the cavern map.
    """

    debug = app.config.get('DEBUG', False)
    game = Game.from_json(session['game'])
    messages = []
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
            logger.debug(game.wumpus)
        if move == 'e':
            messages, errors = game.hunter.enter(cave_id, game.hazards)
        else:
            messages, errors = game.hunter.shoot(cave_id, game.hazards)

        # Sadly, flask makes use of client-side sessions in the form of a session cookie.  So the state of the game
        # must be json serializable and small enough to be accommodated in a cookie.
        session['game'] = game.to_json()

    if errors:
        return jsonify({"errors": errors}), 400

    # Note that the relevant cave id for the notebook is the cave in which the hunter is located and not the
    # cave the hunter shoots into (in the event that the hunter took a shot).
    cavern_map = game.hunter.notebook.consult_notebook(game.hunter.cave.id)

    return jsonify({"messages": [message.to_json() for message in messages],
                    "cave_ids": game.hunter.cave.neighboring_caves,
                    "arrows": game.hunter.quiver,
                    "game_over": not(game.wumpus.alive and game.hunter.alive),
                    "notes": Markup(cavern_map)}), 200


@app.route('/rules', methods=['GET'])
def rules():
    """
    Provides a static web page containing the rules of the game.
    :return: game rules page
    """
    return render_template("rules.html")


app.run()
