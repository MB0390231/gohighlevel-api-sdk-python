import os
from dotenv import load_dotenv

load_dotenv()


class HighLevelConfig(object):
    CLIENT_ID = os.environ["CLIENT_ID"]
    CLIENT_SECRET = os.environ["CLIENT_SECRET"]
    API_BASE_URL = "https://services.leadconnectorhq.com"
    AUTH_BASE_URL = "https://marketplace.gohighlevel.com"
    VERSION = "2021-07-28"
    SCOPES = [
        "contacts.readonly",
        "locations.readonly",
        "opportunities.readonly",
        "forms.readonly",
    ]
    REDIRECT_URI = "http://localhost:3000/oauth/callback"
