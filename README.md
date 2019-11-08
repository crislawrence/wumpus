# Hunt the Wumpus
Browser based version of the original hunt the wumpus game.

## Setup for Stand Alone Use

The instructions below relate principally to installations on Mac or Linux machines.

In a directory of your choice, do a git clone of the wumpus repository.

```bash
cd <directory path>
git clone git@github.com:crislawrence/wumpus.git
```

Enter the project and set up a virtual environment using python 3.6+ (assuming the resident
python 3.6+ version is in python3).

```bash
cd <directory path>/wumpus
python3 -m venv ./venv
```

Activate the virtual environment and install the requirements.

```bash
source venv/bin/activate
pip install -r requirements.txt
```

Copy the .env_example to .env and fill in the .env (note the parent here refers to the parent location for uploads,
database, db backups and logs discussed earlier):

```bash
cp .env_example .env
```

```
APPLICATION_SETTINGS=config_default.py (for development) or config.py (for production)
SECRET_KEY=<Provide a character string to use as a key for the session cookie>
LOG_FILE=<location for log files.  Remove the entry to default logging to logs/wumpus.log.>
LOG_LEVEL=<DEBUG, WARN, ERROR>.  Remove the entry to default to WARN
SEED=<Provide a seed value if reproducible results are desired.  Otherwise, remove the entry>
```

Finally, you will need to install graphviz.  I use homebrew on the Mac:

```bash
brew install graphviz
```

Hopefully with this much in place, you can start the server from the top level of the wumpus
project with python app.py (while in the venv).  The home page is on localhost:5000.
