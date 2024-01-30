from fastapi import FastAPI, Request

app = FastAPI()

from router.google_auth_router import router as google_auth_router
from router.slack_auth_router import router as slack_auth_router
from router.interactivity_router import router as interactivity_router

app.include_router(interactivity_router)
app.include_router(google_auth_router)
app.include_router(slack_auth_router)


@app.get("/")
def hello():
    return "Choi"
