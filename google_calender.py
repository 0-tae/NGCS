from flask import Flask, request, make_response
import requests
import slackbot_info as sb_info
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import calendar as module_calendar
import os.path
import pytz
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
SEOUL_TIMEZONE = pytz.timezone('Asia/Seoul')


class GoogleCalendarAPI:
  creds = None
  instance = None

  def __init__(self):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
      self.creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not self.creds or not self.creds.valid:
      if self.creds and self.creds.expired and self.creds.refresh_token:
        self.creds.refresh(Request())
      else:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES
        )
        self.creds = flow.run_local_server(port=0)
      # Save the credentials for the next run
      with open("token.json", "w") as token:
        token.write(self.creds.to_json())
    
    self.instance = build("calendar", "v3", credentials=self.creds)


  # 캘린더에 일정 등록

  # 캘린더에 휴가 등록

  # 캘린더에 일정이 등록 되면, 슬랙봇에 출력

  # 캘린더에서 일정을 받아온 후 슬랙봇에 출력

  # 캘린더에서 휴가 받아오기
  # option : 일별, 월별

  # 캘린더에서 일정 받아오기
  # option : 일별, 월별
  def get_events(self, option):
    print("Getting the upcoming 10 events")
    now = datetime.now(SEOUL_TIMEZONE)    


    # "month" 옵션일 때, 해당 월의 스케줄을 가져옴
    # "week" 옵션일 때,  이번 달의 해당하는 한 주차 스케줄을 가져옴 (좀 복잡함)
    # "today" 옵션일 때, 금일의 스케줄을 가져옴(default)

    time_min = now.isoformat()
    time_max = None

    if option == "month":
      last_day_of_month = module_calendar.monthrange(now.year, now.month)[1]
      time_max = datetime(now.year, now.month, last_day_of_month).astimezone(SEOUL_TIMEZONE).isoformat()


    print("TIMEMAX",time_max)
    print("TIMEMIN",time_min)

    events_result = (
        self.instance.events()
        .list(
            calendarId="primary",
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    events = events_result.get("items", [])

    if not events:
      print("No upcoming events found.")
      return

    # Prints the start and name of the next 10 events
    for event in events:
      print(prettier(event))
      start = event["start"].get("dateTime", event["start"].get("date"))
      print(start, event["summary"])



def prettier(data):
  return json.dumps(data, indent=4, separators=(",", ":"), sort_keys=True)

calendar = GoogleCalendarAPI()
calendar.get_events(option="month")
# [END calendar_quickstart]