from flask import Flask, request, make_response
import requests
from datetime import datetime
from bs4 import BeautifulSoup as bs
import slackbot_info as sb_info
from apscheduler.schedulers.background import BackgroundScheduler



CHANNEL_ID = sb_info.get_channel_id('slack-bot')
POSTS = []

app = Flask(__name__)

@app.route('/view_post', methods = ['POST'])
def get_user_id(member_name):
    """
    슬랙 채널ID 조회
    """
    result = self.client.users_list()

    members = result.data['members']

    # 중복된 이름 아직 고려 X
    member = list(filter(lambda m: m["name"] == member_name, members))[0]

    member_id = member["id"]

    return member_id


def get_message_ts(self, channel_id, query):
        """
        슬랙 채널 내 메세지 조회
        """
        # conversations_history() 메서드 호출
        result = self.client.conversations_history(channel=channel_id)
        # 채널 내 메세지 정보 딕셔너리 리스트
        messages = result.data['messages']
        # 채널 내 메세지가 query와 일치하는 메세지 딕셔너리 쿼리
        message_list = list(filter(lambda m: m["text"]==query, messages))

        message_ts = None

        if len(message_list) > 0:
            message_ts = message_list[0]["ts"]
            print('message_ts:',message_ts)
        else:
            print("Message Not Found")
        

        return message_ts

def post_thread_message(self, channel_id, message_ts, text):
        """
        슬랙 채널 내 메세지의 Thread에 댓글 달기
        """
        # chat_postMessage() 메서드 호출
        result = self.client.chat_postMessage(
            channel=channel_id,
            text = text,
            thread_ts = message_ts
        )
        return result


def post_message_user(self, channel_id, user_id):
        response = self.client.chat_postEphemeral(
            channel=channel_id,
            text="안녕하세요 :tada:",
            user=user_id
        )


def post_message(channel_id, text, blocks):
        """
        슬랙 채널에 메세지 보내기
        """
        # chat_postMessage() 메서드 호출
        header = sb_info.get_header()
        data = {"channel":channel_id, "text":text, "blocks":blocks}
        response = requests.post("https://slack.com/api/chat.postMessage", headers = header, json = data)
        print(data)
        print('result:', response.text)

        return response.text
     

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
    app.logger.info("Scheduler -> get_notification")

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


sched = BackgroundScheduler()
sched.add_job(get_notification, 'interval', seconds = 300)
sched.add_job(POSTS.clear, 'cron', hour='12')
sched.start()

if __name__=='__main__':      
      app.logger.info("server on :: PORT="+str(8081))
      app.run(debug = True, user_reloader=False)