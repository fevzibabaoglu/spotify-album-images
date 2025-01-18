class Track:
    def __init__(self, id: str, name: str, artist_names: list[str], album_image_url: str):
        self.id = id
        self.name = name
        self.artist_names = artist_names
        self.album_image_url = album_image_url

    @classmethod
    def from_api_data(cls, track_data):
        """Create a Track object from Spotify API data."""
        id = track_data.get('id', '')
        name = track_data.get('name', '')

        artists = track_data.get('artists', [])
        artist_names = [artist.get('name') for artist in artists if artist.get('name') is not None]

        album_images = track_data.get('album', {}).get('images')
        album_image_url = album_images[0].get('url') if album_images is not None else ''

        return cls(id=id, name=name, artist_names= artist_names, album_image_url=album_image_url)
