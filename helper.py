from os import environ
from dotenv import find_dotenv, load_dotenv
import json

dotenv_file = find_dotenv()
if not dotenv_file:
    f = open('.env', 'x')
    f.close()
    dotenv_file = find_dotenv()
load_dotenv(dotenv_file)  # load secret keys

GOOGLE_CLIENT_SECRET = environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_CLIENT_ID = environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_DISCOVERY_URL = environ.get("GOOGLE_DISCOVERY_URL", None)
APPROVED_EMAILS = json.loads(environ.get("APPROVED_EMAILS", '[]'))
