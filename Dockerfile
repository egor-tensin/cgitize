FROM alpine:3.10

RUN apk add --no-cache bash git openssh-client python3 tini

ARG ssh_sock_dir=/var/run/cgitize
ARG ssh_sock_path="$ssh_sock_dir/ssh-agent.sock"

ENV SSH_AUTH_SOCK "$ssh_sock_path"

COPY ["docker/entrypoint.sh", "/"]
COPY ["cgitize/", "/usr/src/cgitize/"]
WORKDIR /usr/src

ENTRYPOINT ["/sbin/tini", "--", "/entrypoint.sh"]
CMD ["python3", "-m", "cgitize.main"]
