import os
from datetime import timedelta

DEBUG = True
SEED = os.environ.get("SEED", None)
ENV = 'development'
JSONIFY_PRETTYPRINT_REGULAR = False
PROPAGATE_EXCEPTIONS = True
SECRET_KEY = os.environ["SECRET_KEY"]
PERMANENT_SESSION_LIFETIME = timedelta(minutes=300)

