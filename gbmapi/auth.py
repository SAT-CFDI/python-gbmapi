import hashlib
import time
from base64 import urlsafe_b64encode
import pyotp
import requests

from .exceptions import ResponseError
from .utils import generate_secure_base64_string, STANDARD_HEADERS, load_jwt

CLIENT_ID = "7c464570619a417080b300076e163289"


class GBMAuth:
    AUTH_URL = "https://auth.gbm.com"
    ORIGIN = 'https://app.gbm.com'

    def __init__(self, user, password, secret, device, latitude, longitude, device_mac_address, client_id=CLIENT_ID):
        self.client_id = client_id
        self.user = user
        self.password = password
        self.secret = secret
        self.device = device
        self.latitude = latitude
        self.longitude = longitude
        self.device_mac_address = device_mac_address
        self._credentials = None

    @property
    def credentials(self):
        return self._credentials

    @credentials.setter
    def credentials(self, value):
        self._credentials = value

    def check_credentials(self):
        cred = self.credentials
        if cred is None:
            self.login()
            cred = self.credentials
        else:
            _, b, _ = load_jwt(cred['accessToken'])
            if b['exp'] + 60 <= time.time():
                self.refresh()
                cred = self.credentials

        return cred

    def access_token(self):
        cred = self.check_credentials()
        return cred['tokenType'] + ' ' + cred['accessToken']

    def identity_token(self):
        cred = self.check_credentials()
        return cred['identityToken']

    def _request(self, method, path, headers=None, json=None, check_success=True):
        resp = requests.request(
            method,
            self.AUTH_URL + path,
            headers={
                **STANDARD_HEADERS,
                'origin': self.ORIGIN,
                **(headers if headers else {})
            },
            json=json
        )
        if resp.status_code != 200:
            if resp.status_code == 401:
                self.credentials = None
            raise ResponseError(resp)

        resp = resp.json()
        if check_success:
            assert resp['code'] == 0, resp
            assert resp['id'] == "Success", resp
            assert resp['message'] == "Exitoso", resp
        return resp

    def _auth_request(self, method, path, json=None):
        return self._request(
            method,
            path,
            headers={
                'authorization': self.access_token()
            },
            json=json
        )

    def client(self):
        resp = self._request(
            method="GET",
            path=f"/api/v1/clients/{self.client_id}",
        )
        return resp

    def login(self):
        device_headers = {
            'device': self.device,
            'device-latitude': self.latitude,
            'device-longitude': self.longitude,
            'device-mac-address': self.device_mac_address,
            'origin': GBMAuth.AUTH_URL
        }

        # Create a code verifier and challenge
        code_verifier = generate_secure_base64_string(43)
        m = hashlib.sha256()
        m.update(code_verifier.encode())
        code_challenge = urlsafe_b64encode(m.digest()).decode().rstrip("=")

        resp = self._request(
            method="POST",
            path="/api/v1/session/user",
            headers=device_headers,
            json={
                "clientId": self.client_id,
                "user": self.user,
                "password": self.password,
                "responseType": "code",
                "codeChallenge": code_challenge,
                "codeChallengeMethod": "SHA256",
            },
            check_success=False
        )['challengeInfo']

        # Create a TOTP object
        assert resp['challengeType'] == "SOFTWARE_TOKEN_MFA", resp.text
        totp = pyotp.TOTP(self.secret)
        otp = totp.now()

        resp = self._request(
            method="POST",
            path="/api/v1/session/user/challenge",
            headers=device_headers,
            json={
                "challengeType": resp['challengeType'],
                "session": resp['session'],
                "user": self.user,
                "code": otp,
                "clientId": self.client_id,
                "applicationName": "GBM+",
                "responseType": "code",
                "codeChallenge": code_challenge,
                "codeChallengeMethod": "SHA256"
            }
        )

        resp = self._request(
            method="POST",
            path="/api/v1/session/token",
            json={
                "clientId": self.client_id,
                "codeVerifier": code_verifier,
                "code": resp['authorizationCode']
            }
        )
        self.credentials = resp

    def refresh(self):
        cred = self.credentials
        refresh_token = cred['refreshToken']

        resp = self._request(
            method="POST",
            path="/api/v1/session/user/refresh",
            json={
                "clientId": self.client_id,
                "refreshToken": refresh_token
            }
        )
        resp['refreshToken'] = refresh_token
        self.credentials = resp

    # After Authenticated
    def logout(self):
        # Clear Session Token
        self._auth_request(
            "DELETE",
            path=f"/api/v1/session/user?client_id={self.client_id}",
        )
        self.credentials = None

    def security_settings(self):
        """Returns the security settings of the user"""
        return self._auth_request(
            "GET",
            path="/api/v1/security-settings"
        )

    def login_history(self):
        """Returns the login history of the user"""
        return self._auth_request(
            "GET",
            path="/api/v1/security-settings/login-history"
        )

    def challenge(self):
        """Returns information about the challenge."""
        return self._auth_request(
            method="GET",
            path="/api/v1/challenge"
        )

    def token(self):
        """Returns information about the token."""
        return self._auth_request(
            method="GET",
            path="/api/v1/token"
        )
