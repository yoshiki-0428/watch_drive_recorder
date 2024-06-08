variable "project_id" {
  default = "movie-convertor"
}
variable "region" {
  default = "asia-northeast1"
}
variable "cloudrun_image" {
  default = "gcr.io/movie-convertor/my-fastapi-app@sha256:2293c5bc30c98da788eec74372c3d6641956916adfaf757bb3aba25fda75773f"
}
variable "environment" {
  default = "prd"
}