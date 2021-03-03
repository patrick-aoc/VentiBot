import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

class SpotifyTool:

  def __init__(self, id, secret):
    self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=id,
        client_secret=secret))

  async def get_song_info(self, search):

      # Get the song info --> get the song name and also
      # the link to the artist's page
      song = self.sp.track(search)
      info = dict()
      info.update({"name": song["name"]})
      print(info)

      artist_name = song["artists"][0]["name"]
      info.update({"artist": artist_name})

      print(info)
      return info

    
  