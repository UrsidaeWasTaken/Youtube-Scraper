import requests
import configparser
import csv
import json
from time import sleep
from bs4 import BeautifulSoup

config = configparser.ConfigParser()
config.read('config.ini')

API_KEY = config['client']['api_key']
VIDEO_INFO_URL = config['base_url']['video_info']
SEARCH_QUERY_URL = config['base_url']['search_query']
CSV_FILE = config['file']['csv']

# Stores video information in csv
def video_info(video_id, keyword=None):
    url = requests.get(VIDEO_INFO_URL .format(id=video_id, key=API_KEY))
    sleep(1)
    data = url.json()

    # Details of the video
    keyword = keyword.replace("%23", "#")
    keyword = keyword.replace("+", " ")
    keyword = keyword.replace("%2B", "+")
    video_info = data['items'][0]
    video_published = video_info['snippet']['publishedAt'][:10]
    video_channel, video_channel_id = video_info['snippet']['channelTitle'], video_info['snippet']['channelId']
    video_title = video_info['snippet']['title']
    try:
        video_views = video_info['statistics']['viewCount']
        views_disabled = False
    except KeyError:
        video_views = "0"
        views_disabled = True
    try:
        video_likes, video_dislikes = int(video_info['statistics']['likeCount']), int(video_info['statistics']['dislikeCount'])
        video_rating = (video_likes/(video_likes+video_dislikes))*100
        ratings_disabled = False
    except KeyError:
        video_likes = video_dislikes = 0
        video_rating = 0
        ratings_disabled = True
    try:
        video_comments = video_info['statistics']['commentCount']
        comments_disabled = False
    except KeyError:
        video_comments = "0"
        comments_disabled = True
    is_live = video_info['snippet']['liveBroadcastContent']

    video_data = [video_id, video_published, video_title, video_channel_id, video_channel,
    video_views, video_rating, video_likes, video_dislikes, video_comments, views_disabled,
    ratings_disabled, comments_disabled, is_live, keyword]

    with open(CSV_FILE, 'a', encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(video_data)

    return

# Collect top 20 videos with specific keyword in the title
def collect_keyword_search(keyword=None):
    if not keyword:
        keyword = input("Enter keyword to search... ").lower()
    keyword = keyword.replace("#", "%23")
    keyword = keyword.replace("+", "%2B")
    keyword = keyword.replace(" ", "+")
    url = requests.get(SEARCH_QUERY_URL .format(keyword))
    print("Fetching videos...\n")
    sleep(1)
    src = url.content
    soup = BeautifulSoup(src, 'lxml')
    videos = soup.findAll(class_='yt-uix-tile-link')
    print("Adding videos to csv...\n")
    for video in videos:
        if "/watch?v=" in video['href']:
            video_id = video['href'][9:]
            video_info(video_id, keyword)
    return

for keyword in ['python', 'javascript', 'java', 'c++', 'php']:
    collect_keyword_search(keyword)
    print("CSV has been updated...")