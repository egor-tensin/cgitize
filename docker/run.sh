#!/usr/bin/env bash

set -o errexit -o nounset -o pipefail

cd /usr/src
exec python3 -m cgitize.main "$@"
