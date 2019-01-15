import requests
import configparser
import csv
import json
from time import sleep
from bs4 import BeautifulSoup

config = configparser.ConfigParser()
config.read('config.ini')

API_KEY = config['client']['api_key']

def video_info(video_id):
    url = requests.get("https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id=%s&key=%s" % (video_id, API_KEY))
    sleep(1)
    data = url.json()

    # Details of the video
    video_info = data['items'][0]
    video_published = video_info['snippet']['publishedAt'][:9]
    video_channel, video_channel_id = video_info['snippet']['channelTitle'], video_info['snippet']['channelId']
    video_title = video_info['snippet']['title']
    video_views = video_info['statistics']['viewCount']
    video_likes, video_dislikes = int(video_info['statistics']['likeCount']), int(video_info['statistics']['dislikeCount'])
    video_rating = (video_likes/(video_likes+video_dislikes))*100
    video_comments = video_info['statistics']['commentCount']
    is_live = video_info['snippet']['liveBroadcastContent']
    video_data = [video_id, video_published, video_title, video_channel_id, video_channel, video_views, video_rating, video_likes, video_dislikes, video_comments, is_live]

    with open('videos_data.csv', 'a') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(video_data)

    return

# Collect 
def collect_keyword_search(keyword):
    keyword = keyword.replace("+", "%2B")
    keyword = keyword.replace(" ", "+")
    url = requests.get("https://www.youtube.com/results?search_query=allintitle:%s" % keyword)
    sleep(1)
    src = url.content
    soup = BeautifulSoup(src, 'lxml')
    videos = soup.findAll(class_='yt-uix-tile-link')
    print(len(videos))
    for video in videos:
        if "/watch?v=" in video['href']:
            video_id = video['href'][9:]
            video_info(video_id)
    return

collect_keyword_search("Youtube")
print("CSV has been updated...")