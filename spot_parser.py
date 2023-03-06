import spotipy
import tempfile
from spotipy.oauth2 import SpotifyClientCredentials
import os

# Get the credentials from the environment variables
spot_client_id = os.environ.get('SPOTIPY_CLIENT_ID')
spot_client_secret = os.environ.get('SPOTIPY_CLIENT_SECRET')

# Set market
market = 'US'

# If the credentials are not set in the environment variables, ask the user to enter them
if spot_client_id is None or spot_client_secret is None:
    spot_client_id = input('Enter your spotify client id: ')
    spot_client_secret = input('Enter your spotify client secret: ')

# Set the credentials for the spotify api client
client_credentials_manager = SpotifyClientCredentials(client_id=spot_client_id, client_secret=spot_client_secret)

# Set the scope
scope = 'user-library-read'

# Get the username from the environment variables, could be yours or someone using your app
username = os.environ.get('SPOTIPY_USER')

# If the username is not set in the environment variables, ask the user to enter it
if username is None:
    username = input('Enter your Spotify username: ')

# Set the auth manager
auth_manager = spotipy.SpotifyOAuth(scope=scope, username=username, client_id=spot_client_id,
                                    client_secret=spot_client_secret, redirect_uri='http://localhost:8888/callback')

# Set the client
sp = spotipy.Spotify(auth_manager=auth_manager)

# Get the user's choice of playlist or saved tracks from the environment variables
choice = os.environ.get('SPOTIPY_CHOICE')
if choice is None:
    choice = input('Enter your choice: ')

# Evaluate the user's choice of playlist or all of their tracks
if choice == 'saved':
    total = sp.current_user_saved_tracks(limit=1)['total']
else:
    playlists = sp.user_playlists(username)
    for playlist in playlists['items']:
        if playlist['name'] == choice:
            choice = playlist['id']
            found = True
            break
    if not found:
        print('Playlist not found')
        exit()
    total = sp.playlist_items(choice, limit=1)['total']

# Initialize the results list
results = []

# Gather all tracks using int division and a limit of 50
for i in range(total // 50 + 1):
    if choice == 'saved':
        result = sp.current_user_saved_tracks(limit=50, offset=i * 50)
    else:
        result = sp.playlist_items(choice, limit=50, offset=i * 50)
    results.extend(result['items'])

# Creates list of track names, artists, and track ids
track_names = []
track_artists = []
track_ids = []
for item in results:
    track = item['track']
    track_names.append(track['name'])
    track_artists.append(track['artists'][0]['name'])
    track_ids.append(track['id'])

print(track_names)
print(track_artists)
print(track_ids)

# Save the track names, artists, and track ids to a temporary file
with tempfile.NamedTemporaryFile(mode='w+', dir='.', prefix='tracks_', encoding="utf-8") as fp:
    for i in range(len(track_names)):
        fp.write(f'\n{track_names[i]}|{track_artists[i]}|{track_ids[i]}|{market}')
    # Test to see if the file was written to
    fp.seek(0)  # Go back to the beginning of the file
    print(fp.read())  # Print the contents of the file
    # Set the environment variable to the path of the temporary file
    os.environ['SPOTIPY_TRACKS'] = fp.name
