from requests import request
from copy import deepcopy
import json

from highlevel_sdk.config import HighLevelConfig
from highlevel_sdk.exceptions import HighLevelError, HighLevelRequestException
from highlevel_sdk.models.abstract_object import AbstractObject


class ObjectParser(object):
    def parse_single(response, target_class):
        if not target_class:
            raise HighLevelError("Must specify target class when parsing single object")

        data = response
        if isinstance(response["data"], dict):
            data = response["data"]
            return AbstractObject.create_object(data, target_class)
        else:
            raise HighLevelError("Must specify either target class calling object")

    def parse_multiple(response, target_class=None):
        ret = []
        for key in response.keys():
            if key == "meta":
                continue

            if isinstance(response[key], list):
                for json_obj in response[key]:
                    ret.append(ObjectParser.parse_single(json_obj), target_class)
            else:
                ret.append(ObjectParser.parse_single(response[key], target_class))
        return ret


class HighLevelClient(object):
    """
    Encapsulates session attributes and methods to make API calls.
    """

    def __init__(self, access_token) -> None:
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Version": HighLevelConfig.VERSION,
        }

    def _call(self, method, path, data=None):
        path = HighLevelConfig.API_BASE_URL + path
        if method in ("GET", "DELETE"):
            response = request(method, path, headers=self.headers, params=data)
        else:
            response = request(method, path, headers=self.headers, data=data)

        highlevel_response = HighLevelResponse(
            body=response.text,
            headers=response.headers,
            status_code=response.status_code,
            call={"method": method, "path": path, "params": data, "headers": self.headers},
        )

        if highlevel_response.is_error():
            raise highlevel_response.error()

        return highlevel_response


class HighLevelResponse(object):
    """
    Encapsulates response attributes and methods.
    """

    def __init__(self, body, headers, status_code, call) -> None:
        self.body = body
        self.headers = headers
        self.status_code = status_code
        self.call = call

    def is_error(self):
        return self.status_code >= 400

    def error(self):
        if self.is_error():
            return HighLevelRequestException(
                "Call to HighLevel API was unsuccessful.",
                request_context=self.call,
                http_headers=self.headers,
                http_status=self.status_code,
                body=self.body,
            )
        else:
            return None

    def json(self):
        return json.loads(self.body)

    def text(self):
        return self.body

    def __repr__(self):
        return f"<HighLevelResponse {self.status_code} {self.body}>"


class HighLevelRequest(object):
    """
    Encapsulates request attributes and methods
    """

    def __init__(
        self,
        method,
        node,
        endpoint,
        api=None,
        api_type=None,
        target_class=None,
        response_parser=ObjectParser,
    ) -> None:
        """
        Args:
            method : The HTTP method to use for the request.
            node : The node to use for the request.
            endpoint : The endpoint to use for the request.
            api_type (optional): The type of API call to make.
            param_checker (optional): The type checker to use for the request.
            target_class (optional): The class to use for the request.
            response_parser (optional): The parser to use for the response.
        """
        self._method = method
        self._node = node
        self._endpoint = endpoint
        self._api = api
        self._api_type = api_type
        self._path = f"{endpoint}/{node}"
        self._params = {}
        self._target_class = target_class
        self._response_parser = response_parser

    def add_param(self, key, value):
        self._params[key] = self._extract_value(value)
        return self

    def add_params(self, params):
        if params is None:
            return self
        for key in params.keys():
            self.add_param(key, params[key])
        return self

    def _extract_value(self, value):
        if hasattr(value, "export_all_data"):
            return value.export_all_data()
        elif isinstance(value, list):
            return [self._extract_value(item) for item in value]
        elif isinstance(value, dict):
            return dict((self._extract_value(k), self._extract_value(v)) for (k, v) in value.items())
        else:
            return value

    def execute(self):
        params = deepcopy(self._params)
        if self._api_type == "EDGE" and self._method == "GET":
            cursor = Cursor(
                target_objects_class=self._target_class,
                params=params,
                endpoint=self._endpoint,
                api=self._api,
                object_parser=self._response_parser,
            )
            cursor.load_next_page()
            return cursor
        response = self._api.call(
            method=self._method,
            path=self._path,
            params=params,
        )
        if response.error():
            raise response.error()
        if self._response_parser:
            return self._response_parser.parse_single(response.json())
        else:
            return response


class Cursor(object):
    """
    Iterates over pages of data.
    """

    def __init__(self, target_objects_class, params, endpoint, api, object_parser) -> None:
        """
        Args:
            target_objects_class : an instance the AbstractObject class. Must have an ID
            params : The parameters to use for the request.
            node : The node to use for the request.
            endpoint : The endpoint to use for the request.
            object_parser : The parser to use for the response.
        """

        self._target_objects_class = target_objects_class
        self._params = params
        self._endpoint = endpoint
        self._api = api
        self._path = f"{endpoint}"
        self._object_parser = object_parser
        self._queue = []
        self._headers = None
        self._next_page = None
        self._has_next_page = False

    def __repr__(self):
        return str(self._queue)

    def __len__(self):
        return len(self._queue)

    def __iter__(self):
        return self

    def __next__(self):
        if not self._queue and not self.load_next_page():
            raise StopIteration()

        return self._queue.pop(0)

    def __getitem__(self, index):
        return self._queue[index]

    def headers(self):
        return self._headers

    def load_next_page(self):
        """
        populates the queue by querying the api for the next page

        returns True if successful, False otherwise
        """

        response = self._api._call(
            method="GET",
            path=self._path,
            data=self._params,
        )
        self._headers = response.headers()

        body = response.json()
        self._queue = self._object_parser.parse_multiple(body, self._target_objects_class)
        self._has_next_page = body["meta"]["nextPage"] is not None
        self._next_page = body["meta"]["nextPageUrl"]
        self._path = self._next_page

        if not self._has_next_page:
            return False

        return True
