import hashlib
import time
from base64 import urlsafe_b64encode

import pyotp

from .base import GBMApiBase
from .utils import generate_secure_base64_string, load_jwt

CLIENT_ID = "7c464570619a417080b300076e163289"


class GBMAuth(GBMApiBase):
    API_URL = "https://auth.gbm.com"
    ORIGIN = 'https://app.gbm.com'

    def __init__(self, user, password, secret, device, latitude, longitude, device_mac_address,
                 client_id=CLIENT_ID):

        self.client_id = client_id
        self.user = user
        self.password = password
        self.secret = secret
        self.device = device
        self.latitude = latitude
        self.longitude = longitude
        self.device_mac_address = device_mac_address
        self._credentials = None

        super().__init__(self)

    @property
    def credentials(self):
        return self._credentials

    @credentials.setter
    def credentials(self, value):
        self._credentials = value

    def load_credentials(self):
        cred = self.credentials
        if cred is None:
            cred = self.login()
            self.credentials = cred
        else:
            _, b, _ = load_jwt(cred['accessToken'])
            if b['exp'] + 60 <= time.time():
                cred = self.refresh()
                self.credentials = cred

        return cred

    def access_token(self):
        cred = self.load_credentials()
        return cred['tokenType'] + ' ' + cred['accessToken']

    def identity_token(self):
        cred = self.load_credentials()
        return cred['identityToken']

    def client(self):
        resp = self._request(
            path=f"/api/v1/clients/{self.client_id}",
            authenticate=False
        )
        return resp

    def login(self):
        device_headers = {
            'device': self.device,
            'device-latitude': self.latitude,
            'device-longitude': self.longitude,
            'device-mac-address': self.device_mac_address,
            'origin': GBMAuth.API_URL
        }

        # Create a code verifier and challenge
        code_verifier = generate_secure_base64_string(43)
        m = hashlib.sha256()
        m.update(code_verifier.encode())
        code_challenge = urlsafe_b64encode(m.digest()).decode().rstrip("=")

        resp = self._request(
            path="/api/v1/session/user",
            authenticate=False,
            headers=device_headers,
            json={
                "clientId": self.client_id,
                "user": self.user,
                "password": self.password,
                "responseType": "code",
                "codeChallenge": code_challenge,
                "codeChallengeMethod": "SHA256",
            },
        )['challengeInfo']

        # Create a TOTP object
        assert resp['challengeType'] == "SOFTWARE_TOKEN_MFA", resp.text
        totp = pyotp.TOTP(self.secret)
        otp = totp.now()

        resp = self._request(
            path="/api/v1/session/user/challenge",
            authenticate=False,
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
        assert resp['code'] == 0

        resp = self._request(
            path="/api/v1/session/token",
            authenticate=False,
            json={
                "clientId": self.client_id,
                "codeVerifier": code_verifier,
                "code": resp['authorizationCode']
            }
        )
        assert resp['code'] == 0

        return resp

    def refresh(self):
        refresh_token = self.credentials['refreshToken']

        resp = self._request(
            path="/api/v1/session/user/refresh",
            authenticate=False,
            json={
                "clientId": self.client_id,
                "refreshToken": refresh_token
            }
        )
        resp['refreshToken'] = refresh_token
        return resp

    # After Authenticated
    def logout(self):
        # Clear Session Token
        self._request(
            path=f"/api/v1/session/user?client_id={self.client_id}",
            method="DELETE"
        )
        self.credentials = None

    def security_settings(self):
        """Returns the security settings of the user"""
        return self._request(
            path="/api/v1/security-settings"
        )

    def login_history(self):
        """Returns the login history of the user"""
        return self._request(
            path="/api/v1/security-settings/login-history"
        )

    def challenge(self):
        """Returns information about the challenge."""
        return self._request(
            path="/api/v1/challenge"
        )

    def token(self):
        """Returns information about the token."""
        return self._request(
            path="/api/v1/token"
        )
