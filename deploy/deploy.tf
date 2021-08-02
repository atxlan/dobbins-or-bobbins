terraform {
  required_providers {
    nomad = {
      source  = "hashicorp/nomad"
      version = "1.4.11"
    }
  }
}

variable "commit" {}

variable "image" {}

variable "github_token" {
  description = "GitHub token for GHCR auth"
  sensitive   = true
}

variable "github_user" {
  description = "GitHub user for GHCR auth"
  sensitive   = true
}

variable "discord_token" {
  description = "Discord auth token"
  sensitive   = true
}

provider "nomad" {
  address = "http://127.0.0.1:4646"
}

resource "nomad_job" "dorb" {
  jobspec = templatefile(
    "job.hcl.tpl",
    {
      discord_token = var.discord_token,
      image         = var.image,
      commit        = var.commit
    }
  )
}
