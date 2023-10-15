from highlevel_sdk.models.abstract_object import AbstractObject
from highlevel_sdk.client import HighLevelRequest


class Contact(AbstractObject):
    def __init__(self, api=None, id=None):
        super().__init__(api, id)

    def get_endpoint(self):
        if self["id"] is None:
            raise ValueError("Contact must have an id to get endpoint")
        return "/contacts/" + self["id"]


class Form(AbstractObject):
    def __init__(self, api=None, id=None):
        super().__init__(api, id)

    def get_endpoint(self):
        if self["id"] is None:
            raise ValueError("Form must have an id to get endpoint")

        return "/forms/" + self["id"]


class Location(AbstractObject):
    def __init__(self, api=None, id=None):
        super().__init__(api, id)

    def get_endpoint(self):
        if self["id"] is None:
            raise ValueError("Location must have an id to get endpoint")
        return "/locations/" + self["id"]

    def get_contacts(self, params=None):
        request = HighLevelRequest(
            method="GET",
            node=None,
            endpoint="/contacts/",
            api=self.api,
            api_type="EDGE",
            target_class=Contact,
        )

        request.add_params({"location_id": self["id"]})

        return request.execute()

    def get_forms(self, params=None):
        request = HighLevelRequest(
            method="GET",
            node=None,
            endpoint="/forms",
            api=self.api,
            api_type="EDGE",
            target_class=Form,
        )

        request.add_params({"location_id": self["id"]})

        return request.execute()
