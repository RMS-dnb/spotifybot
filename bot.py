

import discord
from discord.ext import tasks
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from discord import Embed
import datetime

# Spotify API setup
SPOTIFY_CLIENT_ID = "add"
SPOTIFY_CLIENT_SECRET = "add"

spotify_auth_manager = SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
)
spotify = spotipy.Spotify(auth_manager=spotify_auth_manager)

# Discord bot setup
DISCORD_BOT_TOKEN = "MTMxMzIzNTAyNzE3MzA0ODM2MA.GCe_eW.HHCRoXEjXz_89iSevNZwKhcWcusUFwHNGF4174"
intents = discord.Intents.default()
bot = discord.Client(intents=intents)

# Spotify Artist ID (for RMS)
ARTIST_ID = "4pJ8HL3kT31Gc3fqXQBG9c"

# Track data in memory
previous_listeners = 0
previous_month_listeners = 0

@bot.event
async def on_ready():
    print(f"{bot.user} is now online!")
    check_spotify_data.start()

@tasks.loop(minutes=5)  # Adjust to your desired frequency
async def check_spotify_data():
    global previous_listeners, previous_month_listeners
    channel_id = add number here  # Replace with your Discord channel ID
    channel = bot.get_channel(channel_id)

    if channel is None:
        print("Error: Channel not found. Check the channel ID or permissions.")
        return

    try:
        # Fetch artist data
        artist = spotify.artist(ARTIST_ID)
        current_listeners = artist['followers']['total']
        genres = ", ".join(artist['genres'])

        # Simulating monthly listeners with a time-based check (adjust if you have more specific data)
        current_month = datetime.datetime.now().month
        monthly_listeners = current_listeners  # This is a placeholder for monthly listeners

        # Fetch top tracks (get up to 50 tracks)
        top_tracks = spotify.artist_top_tracks(ARTIST_ID, country='US')
        top_tracks_message = "\n".join(
            [f"- [{track['name']}]({track['external_urls']['spotify']}) ({track['popularity']} popularity)"
             for track in top_tracks['tracks']]
        )

        # Fetch recent albums
        albums = spotify.artist_albums(ARTIST_ID, album_type='album', limit=5)
        album_message = "\n".join(
            [f"- {album['name']} ({album['release_date']})" for album in albums['items']]
        )

        # Fetch artist's popularity
        artist_popularity = artist['popularity']

        # Get artist's profile image (usually the first image in the list is the best quality)
        artist_image_url = artist['images'][0]['url'] if artist['images'] else None

        # Create an embed for the update
        embed = Embed(title="RMS Spotify Update", color=0x1DB954)
        
        # Add the artist's profile image to the embed
        if artist_image_url:
            embed.set_thumbnail(url=artist_image_url)

        embed.add_field(name="Followers", value=f"{current_listeners:,}", inline=False)
        embed.add_field(name="Genres", value=genres or "No genres available", inline=False)
        embed.add_field(name="Top Tracks", value=top_tracks_message or "No top tracks found", inline=False)
        embed.add_field(name="Recent Albums", value=album_message or "No recent albums found", inline=False)
        embed.add_field(name="Spotify Link", value=f"[RMS on Spotify]({artist['external_urls']['spotify']})", inline=False)

        # Adding artist's popularity
        embed.add_field(name="Artist Popularity", value=f"{artist_popularity} (0-100 scale)", inline=False)

        # Send the embed
        await channel.send(embed=embed)

        # Monthly listeners update
        if current_month != previous_month_listeners:
            await channel.send(f"📅 Monthly listeners updated! Current listeners: {monthly_listeners:,}")
            previous_month_listeners = current_month

        # Notify on listener changes
        if current_listeners != previous_listeners:
            change = current_listeners - previous_listeners
            await channel.send(f"🎵 Listener Update: {change:+,} change in followers!")
            previous_listeners = current_listeners

    except Exception as e:
        print(f"Error fetching data: {e}")

# Run the bot
bot.run(DISCORD_BOT_TOKEN)
