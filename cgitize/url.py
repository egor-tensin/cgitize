# Copyright (c) 2026 Egor Tensin <egor@tensin.name>
# This file is part of the "cgitize" project.
# For details, see https://github.com/egor-tensin/cgitize
# Distributed under the MIT License.

from urllib.parse import quote, urlsplit, urlunsplit


def replace_auth(url, auth):
    username, password = auth
    parts = urlsplit(url)
    netloc = quote(username)
    if password is not None:
        netloc += f":{quote(password)}"
    netloc += f"@{parts.hostname}"
    if parts.port is not None:
        netloc += f":{parts.port}"
    parts = parts._replace(netloc=netloc)
    return urlunsplit(parts)


def remove_auth(url):
    parts = urlsplit(url)
    auth = parts.username, parts.password
    netloc = parts.hostname
    if parts.port is not None:
        netloc += f":{parts.port}"
    parts = parts._replace(netloc=netloc)
    return auth, urlunsplit(parts)
