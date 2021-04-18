#!/bin/sh

set -e

host="localhost"
port="6379"
cmd="$@"

>&2 echo "!!!!!!!! Check port for available !!!!!!!!"

until curl http://"$host":"$port"; do
  >&2 echo "Port is unavailable - sleeping"
  sleep 1
done

>&2 echo "Port is up - executing command"

exec $cmd