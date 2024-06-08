# ベースイメージとして公式の Python イメージを使用
FROM python:3.11-slim-buster

# ワーキングディレクトリの設定
WORKDIR /app

# 必要なパッケージのインストール
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Python アプリケーションのコードをコピー
COPY . .

# 環境変数の設定 (必要に応じて)
ENV PYTHONUNBUFFERED=1

# ポート8080を公開
EXPOSE 8080

# 実行するコマンドを指定 (uvicorn を使用して FastAPI を起動)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
