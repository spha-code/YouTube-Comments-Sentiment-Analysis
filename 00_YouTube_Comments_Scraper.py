from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import json
import csv
import time
import os
from urllib.parse import urlparse, parse_qs

# Import load_dotenv from the dotenv library
from dotenv import load_dotenv

# --- Configuration ---
# Load environment variables from .env file
load_dotenv()

# The API key will now be read from the environment variable 'YOUTUBE_API_KEY'.
# This variable is loaded from the .env file by load_dotenv().
API_KEY = os.getenv('YOUTUBE_API_KEY')
#to debug api functionality
#print(f"DEBUG: API Key loaded (first 5 chars): {API_KEY[:5]}... (last 5 chars): {API_KEY[-5:]}")

# Initialize YouTube API client
try:
    if not API_KEY or API_KEY.strip() == "":
        raise ValueError("YOUTUBE_API_KEY environment variable not set or not found in .env file.")
    youtube = build('youtube', 'v3', developerKey=API_KEY)
except ValueError as e:
    print(f"Configuration Error: {e}")
    print("Please ensure you have a '.env' file in the same directory as the script,")
    print("and it contains 'YOUTUBE_API_KEY=YOUR_ACTUAL_API_KEY_HERE'.")
    print("You can get an API key from the Google Cloud Console.")
    exit()
except HttpError as e: # More specific error handling for API initialization
    print(f"HTTP Error initializing YouTube API client: {e}")
    if e.resp.status == 403:
        print("Access denied. Check API key validity, enabled APIs, and quota limits.")
    exit()
except Exception as e:
    print(f"An unexpected error occurred during API client initialization: {e}")
    print("Please ensure your API key is correct and valid and you have an internet connection.")
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
            "Comment Count": int(statistics.get("commentCount", 0)), # Ensure it's an integer
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

def get_video_comments(video_id, max_results_per_call=100, total_max_comments_limit=None):
    """
    Fetches comments for a given YouTube video ID.
    The total_max_comments_limit argument can be set to the actual comment count
    from video details to optimize the fetching process. If not provided,
    it defaults to a very high number (or fetches as many as possible).
    """
    comments = []
    next_page_token = None
    
    # Use the provided limit, otherwise assume a very high number or fetch all available
    effective_comment_limit = total_max_comments_limit if total_max_comments_limit is not None else float('inf')

    print(f"Fetching comments for video ID: {video_id} (up to {effective_comment_limit} comments)")

    retrieved_count = 0
    while retrieved_count < effective_comment_limit:
        try:
            # Determine the maximum results for the current call, ensuring it doesn't exceed 100
            # and doesn't go beyond the effective_comment_limit
            results_to_fetch = min(max_results_per_call, effective_comment_limit - retrieved_count)
            if results_to_fetch <= 0: # Stop if no more needed
                break
            
            response = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=min(results_to_fetch, 100), # YouTube API maxResults is 100
                pageToken=next_page_token,
                textFormat="plainText"
            ).execute()

            for item in response["items"]:
                if retrieved_count >= effective_comment_limit:
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
            if not next_page_token or retrieved_count >= effective_comment_limit:
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
            # Get the actual comment count from video_details
            comment_count = video_details.get("Comment Count", 0)
            print(f"Video '{video_details['Title']}' has {comment_count} comments.")
            
            # Pass the actual comment count to the get_video_comments function
            comments = get_video_comments(video_id, total_max_comments_limit=comment_count) 
            
            if comments:
                comments_output_file = os.path.join("data", f"video_comments_{video_id}.csv")
                comments_fieldnames = ["author", "text", "likeCount", "publishedAt", "commentId"]
                save_to_csv(comments, comments_output_file, comments_fieldnames)
                print(f"Retrieved {len(comments)} comments.")
            else:
                print("No comments retrieved or an error occurred.")
        else:
            print("Could not retrieve video details, so cannot fetch comments.")


    print("\nScript finished.")