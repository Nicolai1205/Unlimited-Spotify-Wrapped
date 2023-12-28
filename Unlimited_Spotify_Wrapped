# Import necessary libraries
import os
import logging
import requests
from datetime import datetime
import pandas as pd
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import webbrowser
from urllib.parse import urlencode, urlparse, parse_qs
from supabase import create_client, Client

# Setup logging
logging.basicConfig(level=logging.INFO)

# Spotify Authenticator Class
class SpotifyAuthenticator:
    def __init__(self):
        self.client_id = os.environ.get('CLIENT_ID')
        self.client_secret = os.environ.get('CLIENT_SECRET')
        self.redirect_uri = 'http://localhost:3000'
        self.auth_url = 'https://accounts.spotify.com/authorize'
        self.token_url = 'https://accounts.spotify.com/api/token'
        self.server = None
        self.code = None

    def authenticate(self):
        self.start_server()
        self.request_authorization()
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        return self.exchange_code_for_token()

    def start_server(self):
        server_address = ('', 3000)
        self.server = HTTPServer(server_address, RequestHandler)
        self.server.authenticator = self

    def request_authorization(self):
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'scope': 'user-top-read',
            'redirect_uri': self.redirect_uri
        }
        url = f"{self.auth_url}?{urlencode(params)}"
        webbrowser.open(url)

    def exchange_code_for_token(self):
        data = {
            'grant_type': 'authorization_code',
            'code': self.code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        response = requests.post(self.token_url, data=data)
        return response.json().get('access_token')

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url_path = urlparse(self.path)
        query_parameters = parse_qs(url_path.query)
        code = query_parameters.get('code', [None])[0]

        if code:
            self.server.authenticator.code = code
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write("Authorization successful. Please close this tab.".encode())
            threading.Thread(target=self.server.shutdown, daemon=True).start()
        else:
            self.send_response(404)
            self.end_headers()

# Data retrieval and processing functions
def make_spotify_api_call(url, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        logging.error(f"Error making API call to {url}, status code: {response.status_code}")
        return None
    return response.json()

def get_top_items_with_rank(access_token, category, time_range):
    url = f"https://api.spotify.com/v1/me/top/{category}?time_range={time_range}&limit=50"
    response = make_spotify_api_call(url, access_token)
    return [(rank + 1, item['name']) for rank, item in enumerate(response['items'])] if response else []

def get_genre_counts_with_rank(access_token, time_range):
    genre_count = {}
    url = f"https://api.spotify.com/v1/me/top/artists?time_range={time_range}&limit=50"
    response = make_spotify_api_call(url, access_token)
    if response:
        artists = response['items']
        for artist in artists:
            for genre in artist['genres']:
                genre_count[genre] = genre_count.get(genre, 0) + 1
    sorted_genres = sorted(genre_count.items(), key=lambda x: x[1], reverse=True)
    return [(rank + 1, genre, count) for rank, (genre, count) in enumerate(sorted_genres)]

def get_playlists_with_track_count(access_token):
    url = f"https://api.spotify.com/v1/me/playlists"
    response = make_spotify_api_call(url, access_token)
    if response:
        playlists = response['items']
        return [(playlist['name'], make_spotify_api_call(f"https://api.spotify.com/v1/playlists/{playlist['id']}", access_token)['tracks']['total']) for playlist in playlists]
    return []

def create_dataframe_with_rank(data, date_column_name, date_value, item_column_name):
    rows = []
    for time_range, items in data.items():
        for rank, item in items:
            rows.append({date_column_name: date_value, 'Time_Range': time_range, item_column_name: item, 'Rank': rank})
    return pd.DataFrame(rows)

def create_genre_dataframe(genre_data, current_date):
    genre_rows = []
    for time_range, genres in genre_data.items():
        for rank, genre, count in genres:
            genre_rows.append({'Date': current_date, 'Time_Range': time_range, 'Rank': rank, 'Genre': genre, 'Count': count})
    return pd.DataFrame(genre_rows)

# Supabase interaction functions
def init_supabase_client():
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_KEY')
    return create_client(url, key)

def insert_df_to_supabase(client, df, table_name):
    logging.info(f"Inserting data into {table_name}...")
    success = True
    data = df.to_dict(orient='records')
    try:
        response = client.table(table_name).upsert(data, on_conflict="unique_key").execute()
        if hasattr(response, 'error') and response.error:
            logging.error(f"Error inserting data into {table_name}: {response.error}")
            success = False
    except Exception as e:
        logging.error(f"An exception occurred: {e}")
        success = False
    return success

# Main orchestration function
def main():
    try:
        access_token = authenticate_and_get_token()
        if not access_token:
            logging.error("Failed to authenticate with Spotify")
            return

        current_date = datetime.now().date()
        df_artists, df_tracks, df_genres, df_playlists = prepare_data(access_token, current_date)

        client = init_supabase_client()
        tables = {
            'artists': df_artists,
            'tracks': df_tracks,
            'genres': df_genres,
            'playlists': df_playlists
        }

        for table_name, df in tables.items():
            if not insert_df_to_supabase(client, df, table_name):
                logging.error(f"Failed to insert data into {table_name}")

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
