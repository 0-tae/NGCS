from flask import Flask, request, make_response
import requests
from datetime import datetime
from bs4 import BeautifulSoup as bs
import slackbot_info as sb_info
from apscheduler.schedulers.background import BackgroundScheduler
from slackbot_sender import post_message
import time

CHANNEL_ID = sb_info.get_channel_id('slack-bot')
POSTS = []

def make_block(notification_title, notification_url):
    return [
        {
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "업로드된 학사 공지",
				"emoji": True
			}
		},
        {
			"type": "divider"
		},
		{
			"type": "section",
			"text": 
            {
				"type": "mrkdwn",
				"text": '*공지 제목*:\n' + notification_title
			}
		},
        {
			"type": "section",
			"text": 
            {
				"type": "mrkdwn",
				"text": '*바로 가기*:\n' + notification_url
			}
		}
	]

# Scheduled Funtion
def get_notification():
    request_url = "https://computer.cnu.ac.kr/computer/notice/bachelor.do"
    response = requests.get(request_url)
    response.raise_for_status()
    soup = bs(response.text, "html.parser")
    
    # 오늘 날짜
    today = datetime.today().strftime("%Y.%m.%d")[2:]
    
    # 공지 날짜
    date_list = list(enumerate(map((lambda e: e.text.strip()),soup.select('td.b-td-left div.b-m-con span.b-date'))))

    # 공지 번호
    post_num_list = list(enumerate(map((lambda e: e.text.strip()),soup.select('td.b-num-box'))))

    # 공지 내용
    content_list = list(enumerate(map((lambda e: {'title':e.attrs['title'],'href':request_url+e.attrs['href']})
                                      ,soup.select('td.b-td-left div.b-title-box a'))))

    for index, date_element in enumerate(date_list):
          date_text = date_element[-1]
          post_num = post_num_list[index][-1]
          content = content_list[index][-1]

          # 공지가 오늘 날짜이면서, 이미 갱신된 POST가 아닐 경우에만

          if date_text == today and not post_num in POSTS:
                print('content:',content)
                print('today',today,'posted_date:',date_text,'num:',post_num)
                POSTS.append(post_num)
                title = content['title']
                url = content['href']
                block = make_block(notification_title = title, notification_url = url)
                response_text = post_message(channel_id = CHANNEL_ID, text = "오늘의 학사공지 소식입니다.", blocks = block)
                print(response_text)




def main():
    sched = BackgroundScheduler()
    sched.add_job(get_notification, 'interval', seconds = 300)
    sched.add_job(POSTS.clear, 'cron', hour='12')
    sched.start()

    while True:
        time.sleep(0.001)

if __name__ == "__main__":
     main()
