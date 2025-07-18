from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
import csv
import time
import os
from urllib.parse import urlparse, parse_qs

# --- Configuration ---
# IMPORTANT: Replace 'YOUR_API_KEY' with your actual YouTube Data API key.
# For security, consider storing this in an environment variable instead of directly in the script.
API_KEY = 'AIzaSyB6N32Bo8-l-mUf70_co2f2RBO9m-g9YPk'

# Initialize YouTube API client
try:
    youtube = build('youtube', 'v3', developerKey=API_KEY)
except Exception as e:
    print(f"Error initializing YouTube API client: {e}")
    print("Please ensure your API key is correct and valid.")
    exit()

# --- Helper Functions ---

def extract_video_id(youtube_url):
    """
    Extracts the video ID from various YouTube URL formats.
    """
    if "youtu.be/" in youtube_url:
        return youtube_url.split("youtu.be/")[1].split("?")[0]
    elif "youtube.com/watch?v=" in youtube_url:
        query_string = urlparse(youtube_url).query
        query_params = parse_qs(query_string)
        return query_params.get("v", [None])[0]
    elif "youtube.com/embed/" in youtube_url:
        return youtube_url.split("youtube.com/embed/")[1].split("?")[0]
    elif "youtube.com/v/" in youtube_url:
        return youtube_url.split("youtube.com/v/")[1].split("?")[0]
    return None

def get_video_details(video_id):
    """
    Fetches details for a given YouTube video ID.
    """
    print(f"Fetching details for video ID: {video_id}")
    try:
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=video_id
        )
        response = request.execute()

        if not response["items"]:
            print(f"No video found for ID: {video_id}")
            return None

        video_data = response["items"][0]
        snippet = video_data["snippet"]
        statistics = video_data["statistics"]
        content_details = video_data["contentDetails"]

        details = {
            "Video ID": video_id,
            "Title": snippet["title"],
            "Description": snippet["description"],
            "Published At": snippet["publishedAt"],
            "Channel Title": snippet["channelTitle"],
            "Channel ID": snippet["channelId"],
            "Category ID": snippet.get("categoryId", "N/A"),
            "Duration": content_details.get("duration", "N/A"), # e.g., PT1H2M3S
            "View Count": statistics.get("viewCount", 0),
            "Like Count": statistics.get("likeCount", 0),
            "Favorite Count": statistics.get("favoriteCount", 0), # Often 0 as YouTube removed public dislikes
            "Comment Count": statistics.get("commentCount", 0),
            "Tags": ", ".join(snippet.get("tags", []))
        }
        return details

    except HttpError as e:
        print(f"HTTP Error fetching video details: {e}")
        if e.resp.status == 400 and "API key expired" in str(e):
            print("Your API key has expired. Please generate a new one in Google Cloud Console.")
        elif e.resp.status == 403:
            print("Access denied. Check API key validity, enabled APIs, and quota limits.")
        elif e.resp.status == 404:
            print(f"Video with ID '{video_id}' not found or is private/deleted.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while fetching video details: {e}")
        return None

def get_video_comments(video_id, max_results_per_call=100, total_max_comments=20000):
    """
    Fetches comments for a given YouTube video ID, up to a total_max_comments limit.
    """
    comments = []
    next_page_token = None
    print(f"Fetching comments for video ID: {video_id} (up to {total_max_comments} comments)")

    retrieved_count = 0
    while retrieved_count < total_max_comments:
        try:
            response = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=min(max_results_per_call, total_max_comments - retrieved_count, 100), # max 100 per call
                pageToken=next_page_token,
                textFormat="plainText"
            ).execute()

            for item in response["items"]:
                if retrieved_count >= total_max_comments:
                    break
                comment = item["snippet"]["topLevelComment"]["snippet"]
                comments.append({
                    "author": comment["authorDisplayName"],
                    "text": comment["textDisplay"],
                    "likeCount": comment["likeCount"],
                    "publishedAt": comment["publishedAt"],
                    "commentId": item["id"] # Include comment ID for uniqueness
                })
                retrieved_count += 1

            next_page_token = response.get("nextPageToken")
            if not next_page_token or retrieved_count >= total_max_comments:
                break
            time.sleep(0.5)  # Add a small delay to respect API quota and avoid hitting limits too quickly

        except HttpError as e:
            if e.resp.status == 403 and "commentsDisabled" in str(e):
                print(f"Comments are disabled for video ID: {video_id}.")
                break
            print(f"HTTP Error fetching comments: {e}")
            if e.resp.status == 400 and "API key expired" in str(e):
                print("Your API key has expired. Please generate a new one in Google Cloud Console.")
            elif e.resp.status == 403:
                print("Access denied. Check API key validity, enabled APIs, and quota limits.")
            break # Exit on error
        except Exception as e:
            print(f"An unexpected error occurred while fetching comments: {e}")
            break # Exit on error

    return comments

def save_to_csv(data, filename, fieldnames):
    """
    Saves a list of dictionaries to a CSV file.
    """
    # Create the data folder if it doesn't exist
    output_dir = os.path.dirname(filename)
    if output_dir: # Check if there's a directory component
        os.makedirs(output_dir, exist_ok=True)

    with open(filename, "w", newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        if isinstance(data, list):
            writer.writerows(data)
        elif isinstance(data, dict):
            writer.writerow(data) # For single dictionary (video details)
    print(f"Data saved to {filename}")

# --- Main Execution ---

if __name__ == "__main__":
    if API_KEY == 'YOUR_API_KEY':
        print("ERROR: Please replace 'YOUR_API_KEY' in the script with your actual YouTube Data API key.")
        print("You can get an API key from the Google Cloud Console.")
        exit()

    youtube_url = input("Enter the YouTube video URL: ")
    video_id = extract_video_id(youtube_url)

    if not video_id:
        print("Invalid YouTube URL. Please provide a valid video URL.")
    else:
        print(f"\nExtracted Video ID: {video_id}")

        # Fetch and save video details
        video_details = get_video_details(video_id)
        if video_details:
            video_details_output_file = os.path.join("data", f"video_details_{video_id}.csv")
            video_details_fieldnames = list(video_details.keys()) # Get keys dynamically
            save_to_csv(video_details, video_details_output_file, video_details_fieldnames)
            print("-" * 30)

        # Fetch and save comments
        comments = get_video_comments(video_id, total_max_comments=20000) # Adjust total_max_comments as needed
        if comments:
            comments_output_file = os.path.join("data", f"video_comments_{video_id}.csv")
            comments_fieldnames = ["author", "text", "likeCount", "publishedAt", "commentId"]
            save_to_csv(comments, comments_output_file, comments_fieldnames)
            print(f"Retrieved {len(comments)} comments.")
        else:
            print("No comments retrieved or an error occurred.")

    print("\nScript finished.")