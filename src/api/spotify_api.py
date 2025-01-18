from base64 import b64encode

from api.endpoints import TOKEN_URL_ENDPOINT
from api.utils import Utils


class SpotifyAPI:
    def __init__(self):
        self.client_id = Utils.get_or_ask_env('SPOTIFY_CLIENT_ID')
        self.client_secret = Utils.get_or_ask_env('SPOTIFY_CLIENT_SECRET')
        self.access_token = None

    def authenticate(self):
        """Authenticate using the Client Credentials Flow and retrieve an access token."""
        response = Utils.post(
            TOKEN_URL_ENDPOINT,
            headers={
                'Authorization': self.__create_basic_auth_header(),
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data={
                'grant_type': 'client_credentials'
            },
        )
        data = response.json()
        self.access_token = data['access_token']

    def make_request(self, endpoint: str):
        """Make an API request to the Spotify Web API."""
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = Utils.get(endpoint, headers=headers)
        return response.json()
    
    def __create_basic_auth_header(self):
        """Create a Basic Auth header for Spotify API requests."""
        auth_string = f'{self.client_id}:{self.client_secret}'
        auth_base64 = b64encode(auth_string.encode('utf-8')).decode('utf-8')
        return f'Basic {auth_base64}'
