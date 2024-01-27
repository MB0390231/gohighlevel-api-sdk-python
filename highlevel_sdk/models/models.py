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

        Returns:
            A Location Object
        """

        path = "/oauth/locationToken"
        data = {"companyId": self["id"], "locationId": location_id}
        response = self.api._call("POST", path, data=data, token_data=self.token_data)
        token_data = response.json()
        loc = Location(token_data=token_data, id=location_id).api_get()
        return loc

    def get_locations(self):
        """
        Queries the API for locations and returns a list of Location Objects.

        Returns:
            A list of Location Objects
        """

        path = "/locations/search"

        data = {"companyId": self["id"], "limit": 1000}

        request = HighLevelRequest(
            method="GET",
            node=None,
            endpoint=path,
            token_data=self.get_token_data(),
            api=self.api,
            api_type="EDGE",
            target_class=Location,
            response_parser=ObjectParser,
        )
        request.add_params(data)

        return request.execute()


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

    def get_contact(self, contact_id):
        path = f"/contacts"

        request = HighLevelRequest(
            method="GET",
            node=contact_id,
            endpoint=path,
            token_data=self.get_token_data(),
            api=self.api,
            api_type="NODE",
            target_class=Contact,
            response_parser=ObjectParser,
        )

        return request.execute()

    def get_calendars(self):
        request = HighLevelRequest(
            method="GET",
            node=None,
            endpoint="/calendars/",
            token_data=self.get_token_data(),
            api=self.api,
            api_type="EDGE",
            target_class=Calendar,
            response_parser=ObjectParser,
        )
        params = {
            "locationId": self["id"],
        }
        request.add_params(params)

        return request.execute()

    def get_users(self):
        request = HighLevelRequest(
            method="GET",
            node=None,
            endpoint="/users/",
            token_data=self.get_token_data(),
            api=self.api,
            api_type="EDGE",
            target_class=User,
            response_parser=ObjectParser,
        )

        params = {
            "locationId": self["id"],
        }
        request.add_params(params)

        return request.execute()

    def get_contact_appointments(self, contact_id):
        request = HighLevelRequest(
            method="GET",
            node=None,
            endpoint=f"/contacts/{contact_id}/appointments/",
            token_data=self.get_token_data(),
            api=self.api,
            api_type="EDGE",
            target_class=Appointment,
            response_parser=ObjectParser,
        )

        return request.execute()

    def get_opportunities(self, limit=20):
        path = "/opportunities/search"

        request = HighLevelRequest(
            method="GET",
            node=None,
            endpoint=path,
            token_data=self.get_token_data(),
            api=self.api,
            api_type="EDGE",
            target_class=Opportunity,
            response_parser=ObjectParser,
        )

        params = {
            "location_id": self["id"],
            "limit": limit,
        }
        request.add_params(params)

        return request.execute()

    def get_calendar_event(self, event_id):
        path = f"/calendars/events/appointments/{event_id}"

        request = HighLevelRequest(
            method="GET",
            node=None,
            endpoint=path,
            token_data=self.get_token_data(),
            api=self.api,
            api_type="EDGE",
            target_class=CalendarEvent,
            response_parser=ObjectParser,
        )

        return request.execute()


class Appointment(AbstractObject):
    def __init__(self, token_data=None, id=None):
        super().__init__(token_data=token_data, id=id)

    def get_endpoint(self):
        if self["id"] is None:
            raise ValueError("Appointment must have an id to get endpoint")
        return "/appointments/" + self["id"]


class User(AbstractObject):
    def __init__(self, token_data=None, id=None):
        super().__init__(token_data, id)

    def get_endpoint(self):
        if self["id"] is None:
            raise ValueError("User must have an id to get endpoint")
        return "/users/" + self["id"]


class Calendar(AbstractObject):
    def __init__(self, token_data=None, id=None):
        super().__init__(token_data=token_data, id=id)

    def get_endpoint(self):
        if self["id"] is None:
            raise ValueError("Calendar must have an id to get endpoint")
        return "/calendars/" + self["id"]

    def get_events(self, start_date, end_date):
        assert start_date is not None, "Retrieve events requires a start date"
        assert end_date is not None, "Retrieve events requires an end date"

        request = HighLevelRequest(
            method="GET",
            node=None,
            endpoint="/calendars/events/",
            token_data=self.get_token_data(),
            api=self.api,
            api_type="EDGE",
            target_class=CalendarEvent,
            response_parser=ObjectParser,
        )
        params = {
            "calendarId": self["id"],
            "locationId": self["locationId"],
            "startTime": start_date,
            "endTime": end_date,
        }
        request.add_params(params)

        return request.execute()


class CalendarEvent(AbstractObject):
    def __init__(self, token_data=None, id=None):
        super().__init__(token_data=token_data, id=id)

    def get_endpoint(self):
        if self["id"] is None:
            raise ValueError("CalendarEvent must have an id to get endpoint")
        return "/calendars/events/" + self["id"]


class Contact(AbstractObject):
    def __init__(self, token_data=None, id=None):
        super().__init__(token_data=token_data, id=id)

    def get_endpoint(self):
        if self["id"] is None:
            raise ValueError("Contact must have an id to get endpoint")
        return "/contacts/" + self["id"]

    def get_appointments(self):
        contact_id = self["contact"]["id"]

        path = f"/contacts/{contact_id}/appointments"

        request = HighLevelRequest(
            method="GET",
            node=None,
            endpoint=path,
            token_data=self.get_token_data(),
            api=self.api,
            api_type="EDGE",
            target_class=Appointment,
            response_parser=ObjectParser,
        )

        return request.execute()


class Form(AbstractObject):
    def __init__(self, token_data=None, id=None):
        super().__init__(token_data=token_data, id=id)

    def get_endpoint(self):
        if self["id"] is None:
            raise ValueError("Form must have an id to get endpoint")

        return "/forms/" + self["id"]


class Opportunity(AbstractObject):
    def __init__(self, token_data=None, id=None):
        super().__init__(token_data=token_data, id=id)

    def get_endpoint(self):
        if self["id"] is None:
            raise ValueError("Opportunity must have an id to get endpoint")

        return "/opportunities/" + self["id"]
