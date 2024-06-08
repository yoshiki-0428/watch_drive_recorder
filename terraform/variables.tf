variable "project_id" {
  default = "movie-convertor"
}
variable "region" {
  default = "asia-northeast1"
}
variable "cloudrun_image" {
  default = "gcr.io/movie-convertor/my-fastapi-app@sha256:3f147f04a797ba7554db8aefd2dbe3b9b87cad243fcf352319457dae9bf25906"
}
variable "environment" {
  default = "prd"
}
