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

    
  async def get_playlist_songs(self, search):

    playlist = self.sp.playlist(search)
    songs = []

    for song in playlist["tracks"]["items"]:
      song_name = song["track"]["name"]
      song_artist = song["track"]["artists"][0]["name"]
      song_pair = {"name": song_name, "artist": song_artist}
      songs.append(song_pair)

    return songs