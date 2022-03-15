FROM alpine:3.15 AS base

FROM base AS build

RUN apk add --no-cache gcc libffi-dev make musl-dev python3-dev py3-pip

COPY ["requirements.txt", "/tmp/"]
RUN python3 -m venv /tmp/venv && \
    . /tmp/venv/bin/activate  && \
    python3 -m pip install -r /tmp/requirements.txt

FROM base

LABEL maintainer="Egor Tensin <Egor.Tensin@gmail.com>"

RUN apk add --no-cache bash git openssh-client python3 tini

COPY --from=build ["/tmp/venv", "/tmp/venv/"]

ARG ssh_sock_dir=/var/run/cgitize
ARG ssh_sock_path="$ssh_sock_dir/ssh-agent.sock"
ENV SSH_AUTH_SOCK "$ssh_sock_path"

COPY ["docker/entrypoint.sh", "/"]
COPY ["cgitize/", "/usr/src/cgitize/"]
WORKDIR /usr/src

ENTRYPOINT ["/sbin/tini", "--", "/entrypoint.sh"]
CMD ["python3", "-m", "cgitize.main"]
