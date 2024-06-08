from fastapi import FastAPI

from ts_convertor import convert_ts_file

app = FastAPI()


@app.get("/")
def read_root():
    convert_ts_file("/Volumes/MyDriveUSB/movie/drive")
    return {"Hello": "World"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
