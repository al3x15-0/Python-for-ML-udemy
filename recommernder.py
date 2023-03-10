# Import the necessary libraries
import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from pprint import pprint
import webbrowser

# Set up the OAuth credentials
scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

api_service_name = "youtube"
api_version = "v3"
client_secrets_file = "client_secret.json"

# Perform the OAuth authentication
flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
    client_secrets_file, scopes)
credentials = flow.run_console()
youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)

# Define a function to get video recommendations from YouTube
def get_video_recommendations(video_id):
    request = youtube.search().list(
        part="id",
        maxResults=20,
        relatedToVideoId=video_id,
        type="video"
    )
    response = request.execute()
    video_ids = [item['id']['videoId'] for item in response['items']]
    return video_ids

# Define a function to create a playlist of recommended videos
def create_recommendation_playlist(video_id):
    # Get the recommended video IDs
    video_ids = get_video_recommendations(video_id)

    # Create a new playlist
    request = youtube.playlists().insert(
        part="snippet,status",
        body={
          "snippet": {
            "title": "Recommended Videos",
            "description": "A playlist of recommended videos generated by the YouTube API."
          },
          "status": {
            "privacyStatus": "public"
          }
        }
    )
    response = request.execute()
    playlist_id = response['id']
   
    # Add the recommended videos to the playlist
    for video_id in video_ids:
        request = youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "position": 0,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id
                    }
                }
            }
        )
        response = request.execute()
   
    # Return the playlist ID
    return playlist_id

# Call the function to create the playlist of recommended videos
playlist_id = create_recommendation_playlist("VIDEO_ID")

# Get the URLs of the recommended videos
request = youtube.playlistItems().list(
    part="snippet",
    playlistId=playlist_id,
    maxResults=20
)
response = request.execute()
video_links = [f'<a href="https://www.youtube.com/watch?v={item["snippet"]["resourceId"]["videoId"]}">{item["snippet"]["title"]}</a>' for item in response['items']]

# Print the links in a numbered list output to an HTML table
output_html = "<table>"
for i, link in enumerate(video_links):
    output_html += f"<tr><td>{i + 1}.</td><td>{link}</td></tr>"
output_html += "</table>"
print(output_html)

# Open the HTML table in a web browser
with open("output.html", "w") as f:
    f.write(output_html)
webbrowser.open("output.html")