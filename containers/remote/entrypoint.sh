#!/bin/sh
set -eu

test -s /run/kiss-authorized-key
install -m 644 -o root -g root /run/kiss-authorized-key /etc/ssh/kiss_authorized_keys
if [ ! -f /var/lib/kiss-ssh/ssh_host_ed25519_key ]; then
    ssh-keygen -q -t ed25519 -N '' -f /var/lib/kiss-ssh/ssh_host_ed25519_key
fi
mkdir -p /run/sshd
exec /usr/sbin/sshd -D -e
