FROM alpine:3.11

RUN apk --no-cache add bash git openssh-server && \
    echo 'root:root' | chpasswd && \
    git config --global user.name 'Travis CI User' && \
    git config --global user.email 'travis@example.org' && \
    sed -ri 's/^#?PermitRootLogin\s+.*/PermitRootLogin yes/' /etc/ssh/sshd_config

WORKDIR /root

COPY ["ssh/server_key", "/etc/ssh/ssh_host_rsa_key"]
COPY ["ssh/server_key.pub", "/etc/ssh/ssh_host_rsa_key.pub"]
COPY ["ssh/client_key.pub", "./.ssh/authorized_keys"]

RUN chmod 0600 -- /etc/ssh/ssh_host_rsa_key && \
    chmod 0700 -- ./.ssh/ && \
    chmod 0600 -- ./.ssh/authorized_keys

COPY ["server/setup_repo.sh", "./"]
RUN ./setup_repo.sh

CMD ["/usr/sbin/sshd", "-D"]
