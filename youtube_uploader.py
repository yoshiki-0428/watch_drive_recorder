# youtube_uploader.py

import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from loguru import logger

# スコープの設定
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def authenticate_youtube():
    creds = None
    # トークンファイルが存在する場合、それをロード
    if os.path.exists("token.json"):
        with open("token.json", "rb") as token:
            creds = pickle.load(token)
    # 認証が無効な場合、再認証
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secrets.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # トークンを保存
        with open("token.json", "wb") as token:
            pickle.dump(creds, token)
    return build("youtube", "v3", credentials=creds)


def upload_video_to_youtube(
    youtube, video_file, title, description, category_id=22, privacy_status="private"
):
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "categoryId": category_id,
        },
        "status": {"privacyStatus": privacy_status},
    }

    media = MediaFileUpload(
        video_file, chunksize=-1, resumable=True, mimetype="video/*"
    )

    request = youtube.videos().insert(
        part="snippet,status", body=body, media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            logger.info(f"Uploading... {int(status.progress() * 100)}%")
    logger.info(f"Upload Complete! Video ID: {response.get('id')}")
    return response.get("id")
