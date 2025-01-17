class Track:
    def __init__(self, id: str, album_image_url: str):
        self.id = id
        self.album_image_url = album_image_url

    @classmethod
    def from_api_data(cls, track_data):
        """Create a Track object from Spotify API data."""
        id = track_data.get('id')
        album_images = track_data.get('album', {}).get('images')
        if album_images is not None:
            album_image_url = album_images[0].get('url')
            return cls(id=id, album_image_url=album_image_url)
