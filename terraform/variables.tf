variable "project_id" {
  default = "movie-convertor"
}
variable "region" {
  default = "asia-northeast1"
}
variable "cloudrun_image" {
  default = "gcr.io/movie-convertor/my-fastapi-app@sha256:a5ff7108019f5523406744a2292872c59f2c250625b6a81a008d54d7a9550fdb"
}
variable "environment" {
  default = "prd"
}
