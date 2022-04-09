FROM nginx:1-alpine AS base

FROM base AS builder

# Install cmark-gfm:
ARG CMARK_GFM_VERSION=0.29.0.gfm.3
ADD ["https://github.com/github/cmark-gfm/archive/refs/tags/$CMARK_GFM_VERSION.zip", "/"]

RUN apk add --no-cache cmake g++ make python2 py3-pip && \
    unzip -- "$CMARK_GFM_VERSION.zip" && \
    cd -- "cmark-gfm-$CMARK_GFM_VERSION" && \
    make INSTALL_PREFIX=/cmark-gfm && \
    make test && \
    make install

# Install the latest Pygments (so that it would highlight CMakeLists.txt, etc.):
ARG PYGMENTS_VERSION=~=2.0

RUN apk add --no-cache py3-pip && \
    pip install --no-cache-dir --target=/pygments "pygments$PYGMENTS_VERSION"

FROM base

RUN apk add --no-cache cgit fcgiwrap python3 spawn-fcgi tini && \
    # Replace the theme with the one I like better:
    grep -q -F -- "style='pastie'" /usr/lib/cgit/filters/syntax-highlighting.py && \
    sed -i -e "s/style='pastie'/style='vs'/" -- /usr/lib/cgit/filters/syntax-highlighting.py

COPY --from=builder ["/cmark-gfm", "/usr/local/"]
COPY --from=builder ["/pygments", "/pygments/"]
ENV PYTHONPATH="/pygments"

COPY ["etc/", "/etc/"]
COPY ["usr/", "/usr/"]
COPY ["cmd.sh", "/"]

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["/cmd.sh"]
