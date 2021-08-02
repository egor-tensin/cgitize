FROM alpine:3.13

RUN build_deps='gcc libffi-dev make musl-dev python3-dev py3-pip' && \
    runtime_deps='bash git openssh-client python3 tini' && \
    apk add --no-cache $build_deps $runtime_deps

ARG ssh_sock_dir=/var/run/cgitize
ARG ssh_sock_path="$ssh_sock_dir/ssh-agent.sock"

ENV SSH_AUTH_SOCK "$ssh_sock_path"

COPY ["requirements.txt", "/tmp/"]
RUN python3 -m venv /tmp/venv && \
    . /tmp/venv/bin/activate  && \
    python3 -m pip install -r /tmp/requirements.txt

COPY ["docker/entrypoint.sh", "/"]
COPY ["cgitize/", "/usr/src/cgitize/"]
WORKDIR /usr/src

ENTRYPOINT ["/sbin/tini", "--", "/entrypoint.sh"]
CMD python3 -m cgitize.main
