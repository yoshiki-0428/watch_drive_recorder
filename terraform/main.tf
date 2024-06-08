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

        image = var.cloudrun_image

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
      timeout_seconds = 1200 # 20分
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

resource "google_eventarc_trigger" "object_created_trigger" {
  name        = "object-created-trigger"
  location    = var.region
  project     = var.project_id
  service_account = google_service_account.movie_convertor.email

  matching_criteria {
    attribute = "type"
    value     = "google.cloud.storage.object.v1.finalized"
  }

  matching_criteria {
    attribute = "bucket"
    value     = google_storage_bucket.video-source.name
  }

  destination {
    cloud_run_service {
      service = google_cloud_run_service.video_editor.name
      path    = "/"  # Cloud Run サービスのパス (必要に応じて変更)
      region  = google_cloud_run_service.video_editor.location
    }
  }
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
