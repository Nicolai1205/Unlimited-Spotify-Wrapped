<h2>Visualization examples</h2>
<p>Example of a visualization of data using Plotly</p>
<img width="968" alt="image" src="https://github.com/Nicolai1205/Unlimited_Spotify_Wrapped/assets/100568658/a0672fd3-ac5a-4d64-b59a-5618ce351bb4">

<br>
<br>

[Trevor.io daily refresh dashboard](https://app.trevor.io/share/dashboard/9aefaaf4-eab0-41dd-84ce-33dcd7c6d4b8/load.html?pin=80edf)
<br>
![image](https://github.com/Nicolai1205/Unlimited-Spotify-Wrapped/assets/100568658/e13f9e0c-82d9-4d34-b890-84f1234fe21b)


## Inspiration

This project was inspired by [@izayl spotify-box](https://github.com/izayl/spotify-box).
This repository was my first look at the possibilities the Spotify API and its usage.

<h1>Unlimited Spotify Wrapped</h1>
<p>I've created this Python application out of my passion for music and data. It's my personal take on Spotify's Wrapped feature, delving into your musical journey. By tapping into Spotify's Web API, my script uncovers unique insights about your favorite tunes and artists, reflecting your musical tastes and listening habits.</p>

<br>

<h2>Features</h2>
<ul>
    <li>Insight into user's top tracks, artists, genres and basic playlist information.</li>
    <li>Automated daily data collection and processing.</li>
    <li>Integration with Supabase for data storage and management.</li>
    <li>Coded without the use of the Spotipy Python package.</li>
    <li>Simple dashboard with linecharts to track changes in music preferences. Free hosting & creation on <a href="https://trevor.io/">Trevor.io</a>.</li>
</ul>

<br>

<h2>Setup and Installation</h2>
<p>Instructions on setting up the project, including environment setup, dependencies, and initial configuration.</p>

<details>
<summary><strong>Spotify Authorization Guide</strong></summary>
<p>

Follow these steps to authorize your application to access Spotify's API.

<strong>Step 1: Create a New Spotify Application</strong>
<ul>
<li>Go to the <a href="https://developer.spotify.com/dashboard/applications">Spotify Developer Dashboard</a>.</li>
<li>Log in and create a new application.</li>
<li>Note your <code>Client ID</code> and <code>Client Secret</code>.</li>
<li>Click on <code>Edit Settings</code> and add <code>http://localhost:3000</code> to the Redirect URIs.</li>
</ul>

<br> 

<strong>Step 2: Obtain Authorization Code</strong>
<ul>
<li>Replace <code>$CLIENT_ID</code> with your actual Client ID in the URL below:
<pre>https://accounts.spotify.com/authorize?client_id=$CLIENT_ID&response_type=code&redirect_uri=http:%2F%2Flocalhost:3000&scope=user-read-currently-playing%20user-top-read</pre></li>
<li>Visit the modified URL, agree to allow access, and you'll be redirected to <code>http://localhost:3000?code=$CODE</code>.</li>
<li><code>$CODE</code> in the URL is your Authorization Code.</li>
</ul>

<br>

<strong>Step 3: Acquire Access Token</strong>
<ul>
<li>With your <code>Client ID</code>, <code>Client Secret</code>, and the <code>Authorization Code</code> from the previous steps, run the following command in your terminal:
<pre>curl -X POST -d client_id=$CLIENT_ID -d client_secret=$CLIENT_SECRET -d grant_type=authorization_code -d code=$CODE -d redirect_uri=http://localhost:3000 https://accounts.spotify.com/api/token</pre></li>
<li>This will return your <code>access_token</code> and <code>refresh_token</code>.</li>
</ul>

<strong>Example response:</strong>
<pre>{
    "access_token": "BQBi-jz...yCVzcl",
    "token_type": "Bearer",
    "expires_in": 3600,
    "refresh_token": "AQCBvdy70...KvnrVIxe...",
    "scope": "user-read-currently-playing user-top-read"
}</pre>

<strong>Note:</strong> If you don't receive a <code>refresh_token</code>, repeat Step 2.

</p>
</details>

<br>

<details>
<summary><strong>Supabase Setup Guide</strong></summary>
<p>

Follow these steps to sign up for Supabase and set up a PostgreSQL database.

<br>

<strong>Step 1: Sign Up for Supabase</strong>
<ul>
<li>Visit the <a href="https://supabase.com/">Supabase website</a>.</li>
<li>You can get a free database set up with Supabase with up to 256 MB</li>
<li>Click on the "Start your project" button.</li>
</ul>

<br>

<strong>Step 2: Create a New Project</strong>
<ul>
<li>Once logged in, click on "New Project".</li>
<li>Fill in the project details, including the project name and database password. Remember to save the password securely, as you will need it to access your database.</li>
<li>Select the region closest to you for the best performance.</li>
<li>Click "Create Project" and wait for your project to be provisioned.</li>
</ul>

<br>

<strong>Step 3: Obtain Project Secrets</strong>
<ul>
<li>After your project is ready, go to the "Settings" tab in your project's dashboard.</li>
<li>Under "API", you will find your project's URL and anon key, which are needed to interact with your Supabase project.</li>
</ul>

<br>

<strong>Step 4: Set Up the Database</strong>
<ul>
<li>In your project's dashboard, navigate to the "SQL" section to manage your database.</li>
<li>You can use the following SQL scripts to create tables for artists, tracks, genres, and playlists:</li>
</ul>
<pre><code>
-- Creating table for artists
CREATE TABLE artists (
    unique_key VARCHAR(700) PRIMARY KEY,
    date DATE NOT NULL,
    time_range VARCHAR(50) NOT NULL,
    artist_name VARCHAR(255) NOT NULL,
    rank INT NOT NULL
);

-- Creating table for tracks
CREATE TABLE tracks (
    unique_key VARCHAR(700) PRIMARY KEY,
    date DATE NOT NULL,
    time_range VARCHAR(50) NOT NULL,
    track_name VARCHAR(255) NOT NULL,
    rank INT NOT NULL
);

-- Creating table for genres
CREATE TABLE genres (
    unique_key VARCHAR(700) PRIMARY KEY,
    date DATE NOT NULL,
    time_range VARCHAR(50) NOT NULL,
    genre_name VARCHAR(255) NOT NULL,
    count INT NOT NULL,
    rank INT NOT NULL
);

-- Creating table for playlists
CREATE TABLE playlists (
    unique_key VARCHAR(700) PRIMARY KEY,
    date DATE NOT NULL,
    playlist_name VARCHAR(255) NOT NULL,
    total_tracks INT NOT NULL
);
</code></pre>
<br>

<strong>Step 5: Use Supabase in Your Application</strong>
<ul>
<li>To connect your application to Supabase, you'll need the URL and keys obtained from Step 3.</li>
<li>Refer to the <a href="https://supabase.com/docs/reference/python/introduction">Supabase documentation</a> for guides on integrating with Python.</li>
</ul>

</p>
</details>

<br>

<details>
<summary><strong>Setting Up Environmental Secrets in GitHub</strong></summary>
<p>

This guide details the process of setting up environmental secrets for a GitHub repository, specifically for a project that utilizes Supabase and Spotify.

<br>

<strong>Environmental Secrets Overview</strong>
<ul>
<li><code>SUPABASE_KEY</code>: Your Supabase key, used for authenticating requests to your Supabase project.</li>
<li><code>SUPABASE_URL</code>: The URL of your Supabase project, required to connect to your Supabase database.</li>
<li><code>CLIENT_ID</code>: Your Spotify application's Client ID, used for Spotify API authentication.</li>
<li><code>CLIENT_SECRET</code>: Your Spotify application's Client Secret, used alongside the Client ID for Spotify API authentication.</li>
<li><code>REFRESH_TOKEN</code>: A Spotify token that allows your application to refresh the access token when it expires.</li>
</ul>

<br>

<strong>Step 1: Adding Secrets to GitHub</strong>
<ul>
<li>Navigate to your GitHub repository.</li>
<li>Click on 'Settings' and then choose 'Secrets and variables' from the left sidebar.</li>
<li>Select 'New repository secret' to add each of the environmental secrets.</li>
<li>Enter the name of the secret (e.g., 'SUPABASE_KEY') and its corresponding value.</li>
<li>Repeat for each secret: 'SUPABASE_URL', 'CLIENT_ID', 'CLIENT_SECRET', and 'REFRESH_TOKEN'.</li>
</ul>

</p>
</details>

<br>

<h2>Important to know</h2>
<p>Juicy little notes.</p>
<ul>
<li>If you are aiming to visualize your data in Jupyter Notebooks, you may find that only 1000 rows are returned from Supabase. This limitation can be changed under the Supabase Settings, API, at the bottom and increasing max rows.</li>
<li>There is a online dashboard to track changes over time. I also have a jupyter notebook I can share with the start for visualizing data using Plotly</li>
</ul>

<br>

<h2>Contact</h2>
<p>Feel free to contact me on any of the social platforms linked on my profile if you have any questions regarding this project.</p>

<br>

<h2>Next steps</h2>
<p>Cleaning up the code removing redundancies</p>




