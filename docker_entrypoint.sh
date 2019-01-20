#!/bin/bash
set -e

/etc/init.d/dbus start
/etc/init.d/avahi-daemon start

exec "$@"