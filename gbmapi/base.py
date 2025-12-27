import requests

from .exceptions import ResponseError
from .utils import STANDARD_HEADERS


class GBMApiBase:
    API_URL = None  # "https://api.gbm.com"
    ORIGIN = None  # "https://homebroker.gbm.com"

    def __init__(self, auth):
        self.auth = auth

    def _request(self, path, method=None, headers=None, json=None, check_success=False, authenticate=True):
        resp = requests.request(
            method if method else ("GET" if json is None else "POST"),
            self.API_URL + path,
            headers={
                **STANDARD_HEADERS,
                **({'authorization': self.auth.access_token()} if authenticate else {}),
                'origin': self.ORIGIN,
                **(headers if headers else {})
            },
            json=json
        )

        if resp.status_code != 200:
            raise ResponseError(resp)

        resp = resp.json()
        if check_success:
            assert resp['code'] == 0, resp
            assert resp['id'] == "Success", resp
            assert resp['message'] == "Exitoso", resp
        return resp
