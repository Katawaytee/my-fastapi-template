from app import template
from app.core.response import ResponseException, ReturnStatus
from app.settings import config
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

ROOT_PATH = config.ROOT_PATH

app = FastAPI(title="my-fastapi-template")

app.include_router(template.router, prefix=ROOT_PATH + "/template")


@app.get(ROOT_PATH)
def about():
    return {"AppName": app.title}


@app.exception_handler(ResponseException)
async def response_exception_handler(request: Request, exc: ResponseException):
    return JSONResponse(
        status_code=exc.code,
        content={
            "status": ReturnStatus.FAIL.value,
            "info": exc.info,
        },
    )
