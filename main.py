import shutil

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi_cloudevents import CloudEvent, install_fastapi_cloudevents
from google.cloud import storage
from loguru import logger
import json
from ts_convertor import convert_ts_file

app = FastAPI()
app = install_fastapi_cloudevents(app)


def download_blob(bucket_name, source_blob_name, destination_file_name):
    """GCS からファイルをダウンロードする関数"""
    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    logger.info(f"Blob {source_blob_name} downloaded to {destination_file_name}.")

    # zipファイルを展開する
    if destination_file_name.endswith(".zip"):
        shutil.unpack_archive(destination_file_name, "input")
        logger.info(f"Unzipping {destination_file_name}...")


@app.post("/")
async def on_event(event: CloudEvent, background_tasks: BackgroundTasks):
    try:
        # eventをすべてログ表示
        logger.debug(
            f"Received event: {event.json}, type: {event.type}, dataschema: {event.dataschema}"
        )

        # リクエストボディが空の場合、エラーを返す
        if event is None:
            raise HTTPException(status_code=400, detail="Request body is empty")

        bucket_name: str = event.data.get("bucket")
        file_name: str = event.data.get("name")

        logger.info(f"Received event for file: gs://{bucket_name}/{file_name}")

        download_blob(bucket_name, file_name, f"input/{file_name}")

        # 変換処理を非同期実行
        background_tasks.add_task(convert_ts_file, "input")

        return {"message": "Event received and processed successfully."}
    except (KeyError, json.JSONDecodeError) as e:
        logger.error(f"Invalid event data: {e}")
        raise HTTPException(status_code=400, detail="Invalid event data")
    except Exception as e:
        logger.error(f"Error processing event: {e}")
        raise HTTPException(status_code=204, detail="Not found resource")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
