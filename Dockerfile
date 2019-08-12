FROM alpine:3.10

RUN apk add --no-cache git openssh-client python3

ARG ssh_sock_dir=/var/run/cgit-repos
ARG ssh_sock_path="$ssh_sock_dir/ssh-agent.sock"

ENV SSH_AUTH_SOCK "$ssh_sock_path"

COPY ["pull/", "/usr/src/pull/"]
WORKDIR /usr/src

CMD ["python3", "-m", "pull.main"]
