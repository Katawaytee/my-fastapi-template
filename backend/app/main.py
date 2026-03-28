from app import template
from app.settings import config
from fastapi import FastAPI

ROOT_PATH = config.ROOT_PATH

app = FastAPI(title="my-fastapi-template")

app.include_router(template.router, prefix=ROOT_PATH + "/template")


@app.get(ROOT_PATH)
def about():
    return {"AppName": app.title}
