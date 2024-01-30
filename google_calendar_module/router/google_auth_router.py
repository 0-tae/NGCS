from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from domain.google.google_auth import google_auth
from view.apphome.apphome import apphome
from schemas import HttpResponse

router = APIRouter()


# 파라미터로 state, code등의 정보를 가져옴
# 토큰을 생성
@router.get("/api/auth/google/callback")
async def handling_oauth2(request: Request):
    response_url = str(request.url)
    user_id = google_auth.get_temp_user()

    print("URL:", response_url)
    google_auth.user_register(auth_response_url=response_url, user_id=user_id)

    apphome.refresh_single_app_home(user_id=user_id)
    return HTMLResponse("<p> 연동완료 창을 닫아주세요. <p>", status_code=200)


# 연동하기 버튼에 작성된 URL
# auth_url 생성하여 리다이렉트
@router.get("/api/auth/google/link")
def redirect_auth_url():
    auth_url = google_auth.get_auth_url()
    return RedirectResponse(url=auth_url, status_code=303)
