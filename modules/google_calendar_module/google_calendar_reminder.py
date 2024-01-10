import requests
from datetime import datetime
from bs4 import BeautifulSoup as bs
from apscheduler.schedulers.background import BackgroundScheduler
import time

CHANNEL_ID = sb_info.get_channel_id("slack-bot")
POSTS = []


# Scheduled Funtion
def get_notification():
    request_url = "https://computer.cnu.ac.kr/computer/notice/bachelor.do"
    response = requests.get(request_url)
    response.raise_for_status()
    soup = bs(response.text, "html.parser")

    # 오늘 날짜
    today = datetime.today().strftime("%Y.%m.%d")[2:]

    # 공지 날짜
    date_list = list(
        enumerate(
            map(
                (lambda e: e.text.strip()),
                soup.select("td.b-td-left div.b-m-con span.b-date"),
            )
        )
    )

    # 공지 번호
    post_num_list = list(
        enumerate(map((lambda e: e.text.strip()), soup.select("td.b-num-box")))
    )

    # 공지 내용
    content_list = list(
        enumerate(
            map(
                (
                    lambda e: {
                        "title": e.attrs["title"],
                        "href": request_url + e.attrs["href"],
                    }
                ),
                soup.select("td.b-td-left div.b-title-box a"),
            )
        )
    )

    for index, date_element in enumerate(date_list):
        date_text = date_element[-1]
        post_num = post_num_list[index][-1]
        content = content_list[index][-1]

        # 공지가 오늘 날짜이면서, 이미 갱신된 POST가 아닐 경우에만

        if date_text == today and not post_num in POSTS:
            print("content:", content)
            print("today", today, "posted_date:", date_text, "num:", post_num)
            POSTS.append(post_num)
            title = content["title"]
            url = content["href"]
            block = make_block(notification_title=title, notification_url=url)
            response_text = post_message(
                channel_id=CHANNEL_ID, text="오늘의 학사공지 소식입니다.", blocks=block
            )
            print(response_text)


class CalendarScheduler:
    __scheduler__ = BackgroundScheduler()
    __scheduler_dict__ = dict()

    # Custom id를 통해 실제 job_id를 가져옴
    def get_job_by_function_id(self, function_id):
        return self.__scheduler_dict__.get(function_id)

    # Custom id를 통해 실제 job_id를 가져옴
    def update_scheduler_dict(self, function_id, job_id):
        self.__scheduler_dict__.update({function_id: job_id})

    # 스케줄 함수 등록
    def add_cron_scheduler(self, function_id, function: function, hour, minute):
        job_id = self.__scheduler__.add_job(
            function, "cron", hour=hour, minute=minute
        ).id
        self.update_scheduler_dict(function_id=function_id, job_id=job_id)

    # 스케줄 함수 등록
    def add_cron_scheduler(
        self, function_id, function: function, seconds, hour=0, minute=0
    ):
        job_id = self.__scheduler__.add_job(
            function, "interval", hour=hour, minute=minute, seconds=seconds
        ).id
        self.update_scheduler_dict(function_id=function_id, job_id=job_id)

    def execute(self):
        self.__scheduler__.start()
