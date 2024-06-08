import os
import shutil

from fastapi import FastAPI, HTTPException
from google.cloud import storage
from loguru import logger
import json
from ts_convertor import convert_ts_file

app = FastAPI()


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
def process_gcs_event(request_body: dict = None):
    try:
        # リクエストボディが空の場合、エラーを返す
        if request_body is None:
            raise HTTPException(status_code=400, detail="Request body is empty")

        bucket_name: str = request_body.get("bucket")
        file_name: str = request_body.get("name")

        logger.info(f"Received event for file: gs://{bucket_name}/{file_name}")

        download_blob(bucket_name, file_name, f"input/{file_name}")

        # 変換処理を実行
        convert_ts_file("input")

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
