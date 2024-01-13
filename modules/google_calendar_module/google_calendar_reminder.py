import requests
from datetime import datetime
from bs4 import BeautifulSoup as bs
from apscheduler.schedulers.background import BackgroundScheduler
import time


class CalendarScheduler:
    def __init__(self, __scheduler__ = BackgroundScheduler(), __scheduler_dict__ = dict()):
        self.__scheduler__ = __scheduler__
        self.__scheduler_dict__ = __scheduler_dict__

    # Custom id를 통해 실제 job_id를 가져옴
    def get_job_by_function_id(self, function_id):
        return self.__scheduler_dict__.get(function_id)

    # Custom id를 통해 실제 job_id를 가져옴
    def update_scheduler_dict(self, function_id, job_id):
        self.__scheduler_dict__.update({function_id: job_id})

    # 스케줄 함수 등록
    def add_cron_scheduler(self, function_id, function, hour, minute):
        job_id = self.__scheduler__.add_job(
            function, "cron", hour=hour, minute=minute
        ).id
        self.update_scheduler_dict(function_id=function_id, job_id=job_id)

    # 스케줄 함수 등록
    def add_interval_scheduler(self, function_id, function, seconds, hour=0, minute=0):
        job_id = self.__scheduler__.add_job(
            function, "interval", hour=hour, minute=minute, seconds=seconds
        ).id
        self.update_scheduler_dict(function_id=function_id, job_id=job_id)

    def execute(self):
        self.__scheduler__.start()


reminder = CalendarScheduler()
