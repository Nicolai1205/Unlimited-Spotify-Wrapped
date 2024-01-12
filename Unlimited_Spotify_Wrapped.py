# Import necessary libraries
import requests
from datetime import datetime, date, timedelta
import pandas as pd
import os
from supabase import create_client, Client

# Function to get an access token using the refresh token
def get_access_token_from_refresh_token(refresh_token):
    token_url = "https://accounts.spotify.com/api/token"
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    
    client_id = os.environ.get('CLIENT_ID')
    client_secret = os.environ.get('CLIENT_SECRET')

    response = requests.post(token_url, data=data, auth=(client_id, client_secret))
    
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        raise Exception(f"Failed to refresh token: {response.json()}")

# Data retrieval and processing functions
def make_spotify_api_call(url, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error making API call to {url}, status code: {response.status_code}")
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
        return [(playlist['name'], make_spotify_api_call(f"https://api.spotify.com/v1/me/playlists/{playlist['id']}", access_token)['tracks']['total']) for playlist in playlists]
    return []

def create_dataframe_with_rank(data, date_column_name, date_value, item_column_name):
    rows = []
    for time_range, items in data.items():
        for rank, item in items:
            row = {
                date_column_name: date_value,
                'Time_Range': time_range,
                item_column_name: item,
                'Rank': rank
            }
            rows.append(row)
    return pd.DataFrame(rows)

def create_genre_dataframe(genre_data, current_date):
    genre_rows = []
    for time_range, genres in genre_data.items():
        for rank, genre, count in genres:
            row = {
                'Date': current_date,
                'Time_Range': time_range,
                'Rank': rank,
                'Genre': genre,
                'Count': count
            }
            genre_rows.append(row)
    return pd.DataFrame(genre_rows)

# Supabase interaction functions
def init_supabase_client(url: str, key: str) -> Client:
    return create_client(url, key)

def create_unique_key(row: pd.Series) -> str:
    return '_'.join(str(value) for value in row.values)

def lowercase_column_names(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [col.lower() for col in df.columns]
    return df

def format_dataframe(df: pd.DataFrame, int_columns: list = None) -> pd.DataFrame:
    if 'date' in df.columns:
        df['date'] = df['date'].apply(lambda x: x.isoformat() if isinstance(x, (datetime, date)) else x)
    df.fillna("Default Value", inplace=True)
    df = convert_int_columns(df, int_columns)
    return df

def convert_int_columns(df: pd.DataFrame, int_columns: list = None) -> pd.DataFrame:
    if int_columns:
        for col in int_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    return df

def insert_df_to_supabase(client: Client, df: pd.DataFrame, table_name: str) -> bool:
    print(f"Inserting data into {table_name}...")
    success = True
    data = df.to_dict(orient='records')
    try:
        response = client.table(table_name).upsert(data, on_conflict="unique_key").execute()
        if hasattr(response, 'error') and response.error:
            print(f"Error inserting data into {table_name}: {response.error}")
            success = False
    except Exception as e:
        print(f"An exception occurred: {e}")
        success = False
    if success:
        print(f"Data insertion into {table_name} complete.")
    return success

def main():    
    # Get Spotify access token using refresh token
    refresh_token = os.getenv('REFRESH_TOKEN')
    access_token = get_access_token_from_refresh_token(refresh_token)

    current_date = datetime.now().date()
    #current_date = (datetime.now() - timedelta(days=1)).date()
    data_artists = {time_range: get_top_items_with_rank(access_token, 'artists', time_range) for time_range in ['short_term', 'medium_term', 'long_term']}
    data_tracks = {time_range: get_top_items_with_rank(access_token, 'tracks', time_range) for time_range in ['short_term', 'medium_term', 'long_term']}
    genre_data = {time_range: get_genre_counts_with_rank(access_token, time_range) for time_range in ['short_term', 'medium_term', 'long_term']}
    df_artists = create_dataframe_with_rank(data_artists, 'Date', current_date, 'Artist')
    df_tracks = create_dataframe_with_rank(data_tracks, 'Date', current_date, 'Track')
    df_genres = create_genre_dataframe(genre_data, current_date)
    df_playlists = pd.DataFrame(get_playlists_with_track_count(access_token), columns=['Playlist Name', 'Total Tracks'])
    df_playlists.insert(0, 'Date', current_date)

    # Initialize Supabase client
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_KEY')
    client = init_supabase_client(supabase_url, supabase_key)
            
    # Prepare and insert dataframes
    tables = {
        'artists': df_artists,
        'tracks': df_tracks,
        'genres': df_genres,
        'playlists': df_playlists
    }

    for table_name, df in tables.items():
        df = lowercase_column_names(df)
        df = format_dataframe(df, ['count'] if table_name == 'genres' else ['rank'])
        df['unique_key'] = df.apply(create_unique_key, axis=1)
        df.rename(columns={'artist': 'artist_name', 'track': 'track_name', 'genre': 'genre_name', 'playlist name': 'playlist_name', 'total tracks': 'total_tracks'}, inplace=True)
        insert_df_to_supabase(client, df, table_name)
        
    return df_artists, df_tracks, df_genres, df_playlists

# Main script execution
if __name__ == "__main__":
    main()
