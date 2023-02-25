FROM alpine:3.17

RUN apk add -q --no-cache bash git openssh-server tini && \
    echo 'root:root' | chpasswd && \
    git config --global user.name 'John Doe' && \
    git config --global user.email 'John.Doe@example.com' && \
    sed -ri 's/^#?PermitRootLogin\s+.*/PermitRootLogin yes/' /etc/ssh/sshd_config

WORKDIR /root

COPY ["ssh/server_key", "/etc/ssh/ssh_host_ed25519_key"]
COPY ["ssh/server_key.pub", "/etc/ssh/ssh_host_ed25519_key.pub"]
COPY ["ssh/client_key.pub", "./.ssh/authorized_keys"]

RUN chmod 0600 -- /etc/ssh/ssh_host_ed25519_key && \
    chmod 0700 -- ./.ssh/ && \
    chmod 0600 -- ./.ssh/authorized_keys

COPY ["git_server/setup_repo.sh", "./"]
RUN ./setup_repo.sh

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["/usr/sbin/sshd", "-D"]
