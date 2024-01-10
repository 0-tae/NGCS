from datetime import datetime
import calendar as module_calendar
import os.path
import pytz

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]
SEOUL_TIMEZONE = pytz.timezone("Asia/Seoul")
PREFIX = "google_calendar_module/tokens"


class GoogleCalendarAPI:
    __instance__ = None
    __access_users__ = dict()
    __temp_user__ = None

    # 버튼 -> google 로그인 -> redirect 로 인한 user_id 정보 손실 방지 목적
    # 이게 최선인가

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
                self.current_creds.refresh(Request())
            # Save the credentials for the next run
            self.write_token(credential=current_creds, user_id=user_id)

        return current_creds

    def write_token(self, credential, user_id):
        with open(f"{PREFIX}/{user_id}-token.json", "w") as token:
            token.write(credential.to_json())

    def get_auth_url(self, user_id):
        flow = InstalledAppFlow.from_client_secrets_file(
            f"{PREFIX}/credentials.json",
            SCOPES,
            redirect_uri="https://38d0-221-158-214-203.ngrok-free.app/api/auth/callback/google",
        )

        # 유저 아이디 임시 저장
        self.set_temp_user(user_id=user_id)

        # 인증 페이지 url
        # 로그인이 끝나면 클라이언트가 redirect_url에 인증정보와 함께 request
        auth_url, _ = flow.authorization_url()

        return auth_url

    # credential에 따라 인스턴스를 교체
    def set_instance(self, creds):
        self.__instance__ = build("calendar", "v3", credentials=creds)

    # auth를 통해 받은 code를 가져옴
    # 유저 아이디를 입력 받으면, 유저에 대한 토큰을 발급
    # 인스턴스를 해당 토큰이 적용된 creds로 교체

    def get_flow(self):
        flow = InstalledAppFlow.from_client_secrets_file(
            f"{PREFIX}/credentials.json",
            SCOPES,
            redirect_uri="https://38d0-221-158-214-203.ngrok-free.app/api/auth/callback/google",
        )

        return flow

    # 유저가 연동을 시도할 때 적용하는 함수
    def user_register(self, auth_code, user_id):
        # 현재 credential에 대한 flow를 가져옴
        flow = self.get_flow()

        # auth_code를 기반으로 토큰 정보를 Fetch하고, credential을 가져옴
        flow.fetch_token(code_verifier=auth_code)
        creds = flow.credentials

        # 토큰을 저장
        self.write_token(credential=creds, user_id=user_id)

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
            self.____instance____.events()
            .insert(calendarId="primary", body=body)
            .execute()
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
    def get_vacation_list(self, day_option):
        result = list(
            filter(
                lambda e: self.is_vacation(e["summary"]),
                self.get_event_list(day_option=day_option),
            )
        )
        return result

    # 캘린더에서 일반 일정 받아오기
    # 일정에서 휴가만 필터링 하는 방식
    # option : 일별, 월별
    def get_common_event_list(self, day_option):
        result = list(
            filter(
                lambda e: not self.is_vacation(e["summary"]),
                self.get_event_list(day_option=day_option),
            )
        )
        return result

    # 캘린더에서 일정 받아오기
    # option : 일별, 월별
    def get_event_list(self, day_option):
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

        # TODO: 아무런 일정이 없을 때 미구현
        if not events:
            return self.make_response(None)

        result = list(map(lambda event: self.make_response(event), events))

        print([event["summary"] for event in result])

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
