FROM alpine:3.16 AS base

FROM base AS build

RUN apk add --no-cache gcc libffi-dev make musl-dev python3-dev py3-pip

COPY ["requirements.txt", "/tmp/"]
RUN pip3 install --no-cache-dir --target=/deps -r /tmp/requirements.txt

FROM base

LABEL maintainer="Egor Tensin <Egor.Tensin@gmail.com>"

RUN apk add --no-cache bash git openssh-client python3 tini

COPY --from=build ["/deps", "/deps/"]
ENV PYTHONPATH="/deps"

ARG ssh_sock_dir=/
ARG ssh_sock_path="$ssh_sock_dir/ssh-agent.sock"
ENV SSH_AUTH_SOCK "$ssh_sock_path"

COPY ["docker/entrypoint.sh", "/"]
COPY ["cgitize/", "/usr/src/cgitize/"]
WORKDIR /usr/src

ENTRYPOINT ["/sbin/tini", "--", "/entrypoint.sh"]
CMD ["python3", "-m", "cgitize.main"]
