# HighLevel - Python API Client

A Python SDK for interacting with the GoHighLevel API version 2.

## Authentication using OAuth

To authenticate with the GoHighLevel API, you can follow the OAuth flow below:

1. Install the required packages using pip:

   ```bash
   pip install -r requirements.txt
   ```

2. You will need to create a HighLevel app and generate some IDs you will need for later. Here are the steps:

- Navigate to https://marketplace.gohighlevel.com/ and sign up for a developer account.
- Once you have created a developer account, go to "My Apps" and click on "Create App".
- Give it a name, make it public or private, and choose whether you need the "Agency" or "Sub-Account" distribution type. Pick both. You won't regret it. This will allow you to generate an agency access token that can be used to retrieve access tokens for sub-accounts without having to go through the OAuth flow again for each sub-account (This wasn't possible until recently and I had to go though the OAuth flow for each sub-account. It was not fun. )

- Click on the app you have just created and you will be directed to the "Settings" page and should see sections for "Scopes", "Redirect URLs", and "Client Keys".

- First you will need to select which scopes your app will need. For example, if you want to use the "Calendar" endpoint to pull information about calendars, then you will need to choose "calendars.readonly". If you need to make updates to calendars, then choose "calendars.readonly". You can find more information about scopes here: https://highlevel.stoplight.io/docs/integrations/lgbsau1maxulb-scopes

- After choosing the scope needed, you will need to add the scope to the config file. Navigate to `config.py` and replace `SCOPE` with the ones you have chosen:

  ```python
  # config.py
  class HighLevelConfig:
      SCOPE = ['scopes_here']
  ```

- Next you will need to add the following redirect URL to your app: "http://localhost:3000/oauth/callback". This is will allow you to retrieve the access token later on.

- Navigate down to "Client Keys" and click "Add". Input a name and copy both the "Client ID" and "Client Secret". It is important that you keep these somewhere safe.

3. Navigate to `config.py` and replace `CLIENT_ID` and `CLIENT_SECRET` with the one generated when creating your HighLevel app:

   ```python
   # config.py
   class HighLevelConfig:
       CLIENT_ID = 'your_client_id'
       CLIENT_SECRET = 'your_client_secret'
   ```

4. Navigate into your terminal and run the following code.

   ```bash
   python highlevel_sdk/auth.py
   ```

5. Open a web browser and navigate to `http://localhost:3000/initiate`. This will initiate the OAuth flow and redirect you to the GoHighLevel authorization page.

6. After granting permission by selecting the sub-account, you will be redirected back to a new page with the following text

```
{
  "access_token": "access_token_here",
  "token_type": "Bearer",
  "expires_in": 86399,
  "refresh_token": "refresh_token_here",
  "scope": "conversations/message.readonly conversations/message.write",
  "userType": "Location",
  "locationId": "location_id_here",
  "companyId": "location_id_here",
  "hashedCompanyId": "hashed_company_id_here",
}
```

You can now use this access token to authenticate your requests to the GoHighLevel API. You will want to edit the auth.py routes to save the access token to a database or file for later use. Additionally, your access token will be short lived, but can be refreshed using the refresh token.

To refresh your access token, you can either use the refresh_token function in the auth.py file to get a new access token or you can use the refresh_token method on any of the HighLevel objects.

You will then want to save the new token data to your database or file for later use. The old access token will still work until it expires, but the old refresh token will no longer work.

```python
from highlevel_sdk.auth import refresh_token

new_token = refresh_token(refresh_token)
```

or

```python
from highlevel_sdk.models.models import Agency
from highlevel_sdk.models.models import Location
from highlevel_sdk.models.models import Contact


Agency.refresh_token()
Location.refresh_token()
Contact.refresh_token()

print(Agency.get_token_data())
{<token data>}
```

For more information about the GoHighLevel API and available endpoints, refer to the official documentation at [GoHighLevel API Documentation](https://highlevel.stoplight.io/docs/integrations/0443d7d1a4bd0-overview).

## Usage: Working with the Agency Object

```python
from highlevel_sdk.models.models import Agency

AGENCY_ACCESS = {
    "access_token": "<YOUR_ACCESS_TOKEN>",
    "companyId": "<YOUR_COMPANY_ID>",
    "expires_in": 86399,
    "hashedCompanyId": "<YOUR_HASHED_COMPANY_ID>",
    "refresh_token": "<YOUR_REFRESH_TOKEN>",
    "scope": "contacts.readonly locations.readonly opportunities.readonly forms.readonly",
    "token_type": "Bearer",
    "userType": "Company"
}

agency = Agency(token_data=AGENCY_ACCESS, id=AGENCY_ACCESS["companyId"])
location_id = "<YOUR_LOCATION_ID>"
location = agency.get_location(location_id=location_id)

print(location)

<Location> {}
```

Replace AGENCY_ACCESS with the token date retrieved from the OAuth flow.

## Usage: Working with Location Objects

```python
from highlevel_sdk.models.models import Location

LOCATION_ACCESS_INFO =  {
    "access_token": "<YOUR_ACCESS_TOKEN>",
    "companyId": "<YOUR_COMPANY_ID>",
    "expires_in": 86399,
    "hashedCompanyId": "<YOUR_HASHED_COMPANY_ID>",
    "locationId": "<YOUR_LOCATION_ID>",
    "refresh_token": "<YOUR_REFRESH_TOKEN>",
    "scope": "contacts.readonly locations.readonly opportunities.readonly forms.readonly",
    "token_type": "Bearer",
    "userType": "Location"
}

location = Location(token_data=LOCATION_ACCESS_INFO, id=LOCATION_ACCESS_INFO["locationId"]).get()

contacts = location.get_contacts(limit=10)
print(contacts)

[<Contact> {}, <Contact> {}, <Contact> {}]
```

Replace LOCATION_ACCESS_INFO with the token date retrieved from the OAuth flow.
