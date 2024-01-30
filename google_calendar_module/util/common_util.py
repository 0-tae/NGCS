import sys, pytz, json, datetime


def UTFToKorean(text):
    return text.encode("UTF-8").decode("UTF-8").replace("+", " ")


def UTFToKoreanJSON(data):
    converted_data = json.dumps(data).replace("+", " ")
    return json.loads(converted_data)


def debug_message(msg):
    # 상위 프레임(이 함수를 호출한 함수)을 가져옴
    BASE_PATH_LENGTH = 5
    frame = sys._getframe(1)
    file_name = frame.f_code.co_filename.split("\\")[-1]
    function_name = frame.f_code.co_name
    print(f"({file_name}) method [{function_name}] : ", msg)


def now():
    SEOUL_TIMEZONE = pytz.timezone("Asia/Seoul")
    return datetime.datetime.now(SEOUL_TIMEZONE)


def get_seconds_gap_from_now(time):
    # TimeZone 정보가 일치해야 연산이 가능하다.
    SEOUL_TIMEZONE = pytz.timezone("Asia/Seoul")
    input_time = time

    if type(input_time) is not datetime.datetime:
        input_time = formmatted_time_to_datetime(time)
    else:
        input_time = input_time.astimezone(SEOUL_TIMEZONE)

    return (now() - input_time).seconds


def formmatted_time_to_datetime(formmated_time):
    SEOUL_TIMEZONE = pytz.timezone("Asia/Seoul")
    return datetime.datetime.strptime(formmated_time, "%Y-%m-%d %H:%M:%S").replace(
        tzinfo=SEOUL_TIMEZONE
    )


def json_prettier(data):
    return json.dumps(data, indent=4, separators=(",", ":"), sort_keys=True)
