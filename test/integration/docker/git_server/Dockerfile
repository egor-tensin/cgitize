FROM alpine:3.24

RUN apk add -q --no-cache bash git openssh-client-common openssh-server tini && \
    echo 'root:root' | chpasswd && \
    sed -ri 's/^#?PermitRootLogin\s+.*/PermitRootLogin yes/' /etc/ssh/sshd_config

USER root
WORKDIR /root

COPY ["git_server/setup.sh", "./"]
RUN ./setup.sh

COPY ["git_server/entrypoint.sh", "/"]
ENTRYPOINT ["/sbin/tini", "--", "/entrypoint.sh"]

CMD ["/usr/sbin/sshd", "-D"]
