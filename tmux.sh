#!/bin/sh

tmux \
  new-session 'pipenv run python3 ./api_server.py' \; \
  split -h 'cd ui && npm test' \; \
  rename-session 'cs5131-project' \; \
  detach-client
#new-session  'jupyter notebook' \; \
