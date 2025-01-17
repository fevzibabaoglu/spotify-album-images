from api.endpoints import PLAYLIST_TRACKS_ENDPOINT
from api.spotify_api import SpotifyAPI
from api.track import Track


class Playlist:
    def __init__(self, spotify_api: SpotifyAPI, playlist_id: str):
        self.spotify_api = spotify_api
        self.playlist_id = playlist_id

    def get_tracks(self):
        """Yield tracks from the playlist."""
        limit = 50
        endpoint = f'{PLAYLIST_TRACKS_ENDPOINT.format(playlist_id=self.playlist_id)}?limit={limit}'

        while endpoint is not None:
            response = self.spotify_api.make_request(endpoint)

            endpoint = response.get('next')
            trackItems = response.get('items')

            for trackItem in trackItems:
                trackDict = trackItem.get('track')
                track = Track.from_api_data(trackDict)
                if track is not None:
                    yield track
