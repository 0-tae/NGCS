from datetime import datetime
import calendar as module_calendar
import os.path
import pytz
import json
from requests_oauthlib import OAuth2Session
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]
SEOUL_TIMEZONE = pytz.timezone("Asia/Seoul")
PREFIX = "google_calendar_module/tokens"
HOST = "https://53eb-221-158-214-203.ngrok-free.app"


class GoogleCalendarAPI:
    __instance__ = None
    __access_users__ = dict()
    __temp_user__ = None
    __temp_state__ = None

    # 버튼 -> google 로그인 -> redirect 로 인한 user_id 정보 손실 방지 임시 방편

    def set_temp_state(self, state):
        self.__temp_state__ = state

    def get_temp_state(self):
        return self.__temp_state__

    def set_temp_user(self, user_id):
        self.__temp_user__ = user_id

    def get_temp_user(self):
        return self.__temp_user__

    def is_certificated(self, user_id):
        return True if self.get_credentials(user_id=user_id) != None else False

    # 유저가 한 번 인증하면 서버에 유저 이름으로 PREFIX를 가진 Token을 저장
    def get_credentials(self, user_id):
        current_creds = None

        if os.path.exists(f"{PREFIX}/{user_id}-token.json"):
            current_creds = Credentials.from_authorized_user_file(
                f"{PREFIX}/{user_id}-token.json", SCOPES
            )

        if current_creds == None:
            return None
        # If there are no (valid) credentials available, let the user log in.
        if not current_creds.valid:
            if current_creds and current_creds.expired and current_creds.refresh_token:
                current_creds.refresh(Request())
            # Save the credentials for the next run
            self.write_token(credential=current_creds, user_id=user_id)

        return current_creds

    def write_token(self, credential, user_id):
        with open(f"{PREFIX}/{user_id}-token.json", "w") as token:
            token.write(credential.to_json())

    def get_redirect_url(self):
        return "https://53eb-221-158-214-203.ngrok-free.app/api/auth/callback/google"

    def get_auth_url(self):
        with open(f"{PREFIX}/credentials.json", "r") as file:
            credentials = json.load(file)["web"]

        client_config = {
            "token_url": credentials["token_uri"],
            "client_secret": credentials["client_secret"],
            "auth_uri": credentials["auth_uri"],
            "client_id": credentials["client_id"],
        }

        oauth2_session = OAuth2Session(
            client_id=client_config["client_id"],
            scope=SCOPES,
            redirect_uri=self.get_redirect_url(),
        )

        authorization_url, state = oauth2_session.authorization_url(
            client_config["auth_uri"],
            # offline for refresh token
            # force to always make user click authorize
            access_type="offline",
            prompt="select_account",
        )

        # 유저 아이디 임시 저장
        self.set_temp_state(state)
        print("request state:", state)
        return authorization_url

    def user_register(self, auth_response_url, user_id):
        with open(f"{PREFIX}/credentials.json", "r") as file:
            credentials = json.load(file)["web"]

        client_config = {
            "token_url": credentials["token_uri"],
            "client_secret": credentials["client_secret"],
            "auth_uri": credentials["auth_uri"],
            "client_id": credentials["client_id"],
        }

        google = OAuth2Session(
            client_config["client_id"],
            redirect_uri=self.get_redirect_url(),
            state=self.get_temp_state(),
        )

        token = google.fetch_token(
            client_config["token_url"],
            client_secret=client_config["client_secret"],
            authorization_response=auth_response_url,
        )

        token_dict = dict()

        token_dict.update({"client_id": client_config["client_id"]})
        token_dict.update({"client_secret": client_config["client_secret"]})

        for key, value in token.items():
            token_dict.update({key: value})

        with open(f"{PREFIX}/{user_id}-token.json", "w") as new_token:
            new_token.write(json.dumps(token_dict))

    # credential에 따라 인스턴스를 교체
    def set_instance(self, creds):
        self.__instance__ = build("calendar", "v3", credentials=creds)

    # user_id를 기반으로 token 파일을 찾고 credential을 가져온 뒤, api_instance에 적용되는 credential을 교체함
    # creds가 반환이 안되었다면... 아직까진 답이 없음
    def set_api_user(self, user_id):
        creds = self.get_credentials(user_id=user_id)

        if creds == None:
            raise ValueError("유저에 대한 토큰이 존재하지 않음")

        self.set_instance(creds=creds)

    # 캘린더에서 일정을 삭제(shortcut), 우선순위 나중

    # 캘린더에서 일정 수정

    # 캘린더에 일정 등록
    # event_request = Dict {summary, start, end, all-day}
    def insert_event(self, event_request):
        body = self.event_request_convert(event_request=event_request)
        events_result = (
            self.__instance__.events().insert(calendarId="primary", body=body).execute()
        )

        print(f"event_inserted: {body['summary']}")
        return events_result

    # event_request를 API 규격에 맞는 body로 변환
    def event_request_convert(self, event_request):
        body = {
            "summary": event_request["summary"],  # 일정 제목
            "location": None,  # 일정 장소
            "description": event_request["description"],  # 일정 설명
            "start": {  # 시작 날짜
                "dateTime": event_request["start"].isoformat(),
                "timeZone": "Asia/Seoul",
            },
            "end": {  # 종료 날짜
                "dateTime": event_request["end"].isoformat(),
                "timeZone": "Asia/Seoul",
            },
        }

        # 상세 시간 일정일 때, datetime 객체를 date_str 형식으로 변환
        if event_request["all-day"]:
            body["start"] = {"date": event_request["start"].date().strftime("%Y-%m-%d")}
            body["end"] = {"date": event_request["end"].date().strftime("%Y-%m-%d")}

        return body

    # 기타 function
    # 오전 오후 시간분석
    def is_AM_range(self, time: datetime):
        am_start_time = 9
        pm_start_time = 12
        return am_start_time < time.hour < pm_start_time

    # 휴가 여부 분석(출력 방식이 다름)
    def is_vacation(self, summary):
        vacation_type = ["반차", "연차"]
        return any(k in summary for k in vacation_type)

    # 캘린더에서 휴가 받아오기
    # 일정에서 휴가만 필터링 하는 방식
    # option : 일별, 월별
    def get_vacation_list(self, user_id, day_option="today"):
        result = list(
            filter(
                lambda e: self.is_vacation(e["summary"]),
                self.get_event_list(user_id, day_option=day_option),
            )
        )
        return result

    # 캘린더에서 일반 일정 받아오기
    # 일정에서 휴가만 필터링 하는 방식
    # option : 일별, 월별
    def get_common_event_list(self, user_id, day_option="today"):
        result = list(
            filter(
                lambda e: not self.is_vacation(e["summary"]),
                self.get_event_list(user_id, day_option=day_option),
            )
        )
        return result

    # 캘린더에서 일정 받아오기
    # option : 일별, 월별
    def get_event_list(self, user_id, day_option="today"):
        # api 사용 유저 변경
        self.set_api_user(user_id)

        # "month" 옵션일 때, 해당 월의 스케줄을 가져옴
        # "week" 옵션일 때,  당월에 해당하는 한 주차 스케줄을 가져옴 (좀 복잡함)
        # "today" 옵션일 때, 금일의 스케줄을 가져옴(default)
        now = datetime.now(SEOUL_TIMEZONE)

        time_min = datetime(year=now.year, month=now.month, day=now.day).astimezone(
            SEOUL_TIMEZONE
        )
        time_max = datetime(
            year=time_min.year, month=time_min.month, day=time_min.day + 1
        ).astimezone(SEOUL_TIMEZONE)

        if day_option == "month":
            last_day_of_month = module_calendar.monthrange(now.year, now.month)[1]
            time_max = datetime(now.year, now.month, last_day_of_month).astimezone(
                SEOUL_TIMEZONE
            )

        print(f"TIME: {time_min} ~ {time_max}")

        events_result = (
            self.__instance__.events()
            .list(
                calendarId="primary",
                timeMin=time_min.isoformat(),
                timeMax=time_max.isoformat(),
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        events = events_result.get("items", [])

        # 아무런 일정이 없을 경우 비어있는 리스트 반환
        if not events:
            return list()

        result = list(map(lambda event: self.make_response(event), events))

        return result

    def make_response(self, event):
        response = {
            "summary": "(제목 없음)"
            if event.get("summary") == None
            else event.get("summary"),
            "start": event["start"].get("dateTime")
            if event["start"].get("dateTime")
            else event["start"].get("date"),
            "end": event["end"].get("dateTime")
            if event["end"].get("dateTime")
            else event["end"].get("date"),
            "creator": event["creator"]["email"],
            "created": event["created"],
            "updated": event["updated"],
            "all-day": False if event["start"].get("dateTime") else True,
        }

        return response


calendarAPI = GoogleCalendarAPI()
