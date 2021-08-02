job "dorb" {
  datacenters = ["sheraton"]

  update {
    max_parallel = 0
  }

  group "server" {
    meta {
      commit = "${commit}"
    }

    task "bot" {
      driver = "docker"

      config {
        image      = "${image}"
        command    = "python3"
        force_pull = true
        args       = ["bot.py"]
      }

      resources {
        cpu    = 1000
        memory = 1024
      }

      env {
        DISCORD_TOKEN = "${discord_token}"
        GIT_COMMIT    =  "${commit}"
      }
    }
  }
}
