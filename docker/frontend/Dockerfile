FROM nginx:1

RUN export DEBIAN_FRONTEND=noninteractive && \
    runtime_deps='cgit cmark-gfm fcgiwrap tini' && \
    apt-get update && \
    apt-get install -y --no-install-recommends $runtime_deps && \
    # Install the latest Pygments (so that it would highlight CMakeLists.txt, etc.):
    apt-get install -y --no-install-recommends python3-pip && \
    pip3 install --no-cache-dir pygments~=2.0 && \
    # Replace the theme with the one I like better:
    grep -q -F -- "style='pastie'" /usr/lib/cgit/filters/syntax-highlighting.py && \
    sed -i -e "s/style='pastie'/style='vs'/" -- /usr/lib/cgit/filters/syntax-highlighting.py

COPY ["etc/", "/etc/"]
COPY ["usr/", "/usr/"]
COPY ["cmd.sh", "/"]

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/cmd.sh"]
