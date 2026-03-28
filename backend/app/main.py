from fastapi import FastAPI

app = FastAPI(title="my-fastapi-template")


@app.get("/")
def about():
    return {"AppName": app.title}
