FROM python:3.13-alpine AS base

FROM base AS deps

RUN apk add -q --no-cache gcc libffi-dev make musl-dev

FROM deps AS deps-amd64
FROM deps AS deps-arm64

FROM deps AS deps-arm

# The cryptography package doesn't distribute pre-built binaries for this
# platform, which is why it's built manually (and requires extra dependencies).
RUN apk add -q --no-cache cargo git openssl-dev rust

# Unless this is set, cargo build fails with out of memory errors for some
# reason. Reference:
#
#     https://github.com/docker/buildx/issues/359#issuecomment-1331443419
#
# This is also the reason to install git as a build dependency.
ENV CARGO_NET_GIT_FETCH_WITH_CLI=true

FROM deps-$TARGETARCH AS build

COPY ["requirements.txt", "/tmp/"]
RUN pip3 install -q --no-cache-dir --target=/deps -r /tmp/requirements.txt

FROM base

LABEL maintainer="Egor Tensin <egor@tensin.name>"

RUN apk add -q --no-cache bash git openssh-client tini

COPY --from=build ["/deps", "/deps/"]
ENV PYTHONPATH="/deps:/usr/src"

ARG ssh_sock_dir=/
ARG ssh_sock_path="$ssh_sock_dir/ssh-agent.sock"
ENV SSH_AUTH_SOCK "$ssh_sock_path"

COPY ["docker/cgitize.sh", "/"]
COPY ["docker/get_output_dir.py", "/"]
COPY ["docker/in_cron.sh", "/"]
COPY ["cgitize/", "/usr/src/cgitize/"]

ENV SCHEDULE_ON_START=1
ENTRYPOINT ["/sbin/tini", "--", "/in_cron.sh"]

WORKDIR /usr/src
CMD ["/cgitize.sh"]

HEALTHCHECK --interval=5m --retries=3 CMD ! test -f /fail
