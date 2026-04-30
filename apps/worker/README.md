# Worker App

`run.py` polls `async_jobs` and executes supported job types (starting with `lesson_compile`).

## Docker

The root `infra/docker/docker-compose.yml` includes a `worker` service that mounts this folder and the API package.
