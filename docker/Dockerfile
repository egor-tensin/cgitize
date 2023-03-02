FROM python:3.10-alpine AS base

FROM base AS build

RUN apk add -q --no-cache gcc libffi-dev make musl-dev

COPY ["requirements.txt", "/tmp/"]
RUN pip3 install -q --no-cache-dir --target=/deps -r /tmp/requirements.txt

FROM base

LABEL maintainer="Egor Tensin <Egor.Tensin@gmail.com>"

RUN apk add -q --no-cache bash git openssh-client tini

COPY --from=build ["/deps", "/deps/"]
ENV PYTHONPATH="/deps:/usr/src"

ARG ssh_sock_dir=/
ARG ssh_sock_path="$ssh_sock_dir/ssh-agent.sock"
ENV SSH_AUTH_SOCK "$ssh_sock_path"

COPY ["docker/get_output_dir.py", "/"]
COPY ["docker/run.sh", "/"]
COPY ["docker/run_cron.sh", "/"]
COPY ["cgitize/", "/usr/src/cgitize/"]

ENV SCHEDULE_ON_START=1
ENTRYPOINT ["/sbin/tini", "--", "/run_cron.sh"]

WORKDIR /usr/src
CMD ["/run.sh"]
