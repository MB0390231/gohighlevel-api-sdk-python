from highlevel_sdk.client import HighLevelClient
from highlevel_sdk.models.models import Location
from dotenv import load_dotenv

load_dotenv()
import os

# client

chester_client = HighLevelClient(
    access_token=os.environ["ACCESS_TOKEN"],
)

location = Location(api=chester_client, id=os.environ["LOCATION_ID"]).get()

contacts = location.get_contacts()
