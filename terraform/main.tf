provider "google" {
  credentials = file("credential.json")
  project     = var.project_id
  region      = var.region
}

resource "google_storage_bucket" "video-source" {
  name          = "video-source-bucket"  # 一意のバケット名
  location      = var.region                 # リージョン (例: "ASIA-NORTHEAST1")
  storage_class = "STANDARD"                 # ストレージクラス (STANDARD, NEARLINE, COLDLINE, ARCHIVE)

  # オプション: バージョン管理
  versioning {
    enabled = false
  }

  # オプション: ライフサイクル管理ルール
  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 3  # 30日後にオブジェクトを削除
    }
  }

  # オプション: Uniform Bucket-Level Access を有効にする
  uniform_bucket_level_access = true
}

resource "google_cloud_run_service" "video_editor" {
  name     = "video-editor"
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/movie-convertor/my-fastapi-app@sha256:b32a75b1a9893b388aa361e22c4ef70088fdf3497367e4e117096413889f71db"

        # 環境変数
        env {
          name  = "SOURCE_BUCKET"
          value = google_storage_bucket.video-source.name  # ソースとなる Cloud Storage バケット名
        }
#         env {
#           name  = "DESTINATION_BUCKET"
#           value = "your-destination-bucket-name"  # 編集後の動画を保存する Cloud Storage バケット名
#         }
        # 必要な環境変数を追加
      }
      service_account_name = google_service_account.movie_convertor.email  # Cloud Run が使用するサービスアカウント
    }
    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale" = "5" # スケーリング上限
#         "run.googleapis.com/cloudsql-instances" = google_sql_database_instance.instance.connection_name # Cloud SQL 接続
      }
    }
  }

  # 必要に応じて、トラフィック分割やスケーリングなどの設定を追加
  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [
    google_project_service.run_api,
  ]
}

# Cloud Run API を有効化
resource "google_project_service" "run_api" {
  service = "run.googleapis.com"

  disable_on_destroy = false
}

# Cloud Run が使用するサービスアカウント
resource "google_service_account" "movie_convertor" {
  account_id   = "movie-convertor-sa"
  display_name = "Video Editor Service Account"
  create_ignore_already_exists = true
}

# サービスアカウントに Cloud Storage へのアクセス権限を付与
# resource "google_project_iam_member" "video_editor_storage_admin" {
#   project = var.project_id
#   role    = "roles/storage.admin"
#   member  = "serviceAccount:${google_service_account.movie_convertor.email}"
# }
#
# resource "google_storage_bucket_iam_member" "video_editor_object_viewer" {
#   bucket = google_storage_bucket.video_source.name
#   role   = "roles/storage.objectViewer"
#   member = "serviceAccount:${google_service_account.movie_convertor.email}"
# }
