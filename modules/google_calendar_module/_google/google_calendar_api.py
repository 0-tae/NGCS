from datetime import datetime
import pytz
from _google.google_auth import google_auth
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.

SEOUL_TIMEZONE = pytz.timezone("Asia/Seoul")


class GoogleCalendarAPI:
    def __init__(
        self,
        __instance__=None,
    ):
        self.__instance__ = __instance__

    # credential에 따라 인스턴스를 교체
    def set_instance(self, creds):
        self.__instance__ = build("calendar", "v3", credentials=creds)

    # user_id를 기반으로 token 파일을 찾고 credential을 가져온 뒤, api_instance에 적용되는 credential을 교체함
    def set_api_user(self, user_id):
        creds = google_auth.get_credentials(user_id=user_id)

        if creds == None:
            raise ValueError(f"유저에 대한 토큰이 존재하지 않음: {user_id}")

        self.set_instance(creds=creds)

    # 캘린더에 일정 등록
    # event_request = Dict {summary, start(datetime), end(datetime), all-day}
    def insert_event(self, event_request, user_id):
        self.set_api_user(user_id)
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
            "description": event_request.get("description"),  # 일정 설명
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

    # 휴가 여부 분석(출력 방식이 다름)
    def is_vacation(self, summary):
        vacation_type = ["반차", "연차"]
        return any(k in summary for k in vacation_type)

    # 캘린더에서 휴가 받아오기
    # 일정에서 휴가만 필터링 하는 방식
    # day-option = date
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
    # day-option = date
    def get_common_event_list(self, user_id, day_option="today"):
        result = list(
            filter(
                lambda e: not self.is_vacation(e["summary"]),
                self.get_event_list(user_id, day_option=day_option),
            )
        )
        return result

    def find_event_by_id(self, user_id, event_id):
        self.set_api_user(user_id)

        try:
            event = (
                self.__instance__.events()
                .get(calendarId="primary", eventId=event_id)
                .execute()
            )
        except HttpError:
            return None

        return self.make_response(event=event)

    # 캘린더에서 일정 받아오기
    # option : 일별, 월별
    def get_event_list(self, user_id, day_option="today"):
        # api 사용 유저 변경
        self.set_api_user(user_id)

        # date를 입력 받았을 때, 해당 일자를 가져옴
        # "today" 옵션일 때, 금일의 스케줄을 가져옴(default)
        selected_date = (
            datetime.now(SEOUL_TIMEZONE) if day_option == "today" else day_option
        )

        time_min = datetime(
            year=selected_date.year, month=selected_date.month, day=selected_date.day
        ).astimezone(SEOUL_TIMEZONE)
        time_max = datetime(
            year=time_min.year,
            month=time_min.month,
            day=time_min.day,
            hour=23,
            minute=59,
        ).astimezone(SEOUL_TIMEZONE)

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
            "id": event["id"],
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
