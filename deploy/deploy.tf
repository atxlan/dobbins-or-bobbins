terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "2.8.0"
    }

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

provider "docker" {
  host = "tcp://127.0.0.1:2375"

  registry_auth {
    address  = "ghcr.io"
    username = var.github_user
    password = var.github_token
  }
}

resource "nomad_job" "wbld" {
  jobspec = templatefile(
    "job.hcl.tpl",
    { github_token  = var.github_token,
      github_user   = var.github_user,
      discord_token = var.discord_token,
      image         = var.image,
      commit        = var.commit
    }
  )
}
