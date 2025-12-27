import requests

from . import GBMAuth
from .exceptions import ResponseError
from .utils import STANDARD_HEADERS


class GBMApiBase:
    API_URL = None  # "https://api.gbm.com"
    ORIGIN = None  # "https://homebroker.gbm.com"

    def __init__(self, auth: GBMAuth):
        self.auth = auth

    def _request(self, path, headers=None, json=None):
        resp = requests.request(
            "GET" if json is None else "POST",
            self.API_URL + path,
            headers={
                **STANDARD_HEADERS,
                'authorization': self.auth.access_token(),
                'origin': self.ORIGIN,
                **(headers if headers else {})
            },
            json=json
        )

        if resp.status_code != 200:
            if resp.status_code == 401:
                self.auth.credentials = None

            raise ResponseError(resp)

        resp = resp.json()
        # assert resp['code'] == 0, resp
        # assert resp['id'] == "Success", resp
        # assert resp['message'] == "Exitoso", resp
        return resp
