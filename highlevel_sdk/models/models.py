from highlevel_sdk.models.abstract_object import AbstractObject
from highlevel_sdk.client import HighLevelRequest
from highlevel_sdk.object_parser import ObjectParser


class Agency(AbstractObject):
    def __init__(self, token_data=None, id=None):
        # id is the company id
        assert token_data is not None, "Agency must have an access token"

        super().__init__(token_data=token_data, id=id)

    def get_endpoint(self):
        # get() is not available for Agency
        raise NotImplementedError("Agency does not have an endpoint")

    def get_location(self, location_id):
        """
        Queries the API for an location access token and returns a Location Object.

        Args:
            company_id (str): The company ID.
            location_id (str): The location ID.
            access_token (str): The agency level access token.

        Returns:
            A Location Object
        """

        path = "/oauth/locationToken"
        data = {"companyId": self["id"], "locationId": location_id}
        response = self.api._call("POST", path, data=data, token_data=self.token_data)
        token_data = response.json()
        loc = Location(token_data=token_data, id=location_id).get()
        return loc


class Location(AbstractObject):
    def __init__(self, token_data=None, id=None):
        super().__init__(token_data=token_data, id=id)

    def get_endpoint(self):
        if self["id"] is None:
            raise ValueError("Location must have an id to get endpoint")
        return "/locations/" + self["id"]

    def get_contacts(self, limit=20):
        request = HighLevelRequest(
            method="GET",
            node=None,
            endpoint="/contacts/",
            token_data=self.get_token_data(),
            api=self.api,
            api_type="EDGE",
            target_class=Contact,
            response_parser=ObjectParser,
        )
        params = {
            "limit": limit,
            "locationId": self["id"],
        }
        request.add_params(params)

        return request.execute()


class Contact(AbstractObject):
    def __init__(self, token_data=None, id=None):
        super().__init__(token_data=token_data, id=id)

    def get_endpoint(self):
        if self["id"] is None:
            raise ValueError("Contact must have an id to get endpoint")
        return "/contacts/" + self["id"]
    
    


class Form(AbstractObject):
    def __init__(self, token_data=None, id=None):
        super().__init__(token_data=token_data, id=id)

    def get_endpoint(self):
        if self["id"] is None:
            raise ValueError("Form must have an id to get endpoint")

        return "/forms/" + self["id"]
