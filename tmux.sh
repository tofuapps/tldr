#!/bin/sh

tmux \
  new-session  'jupyter notebook' \; \
  split -h 'cd ui && npm test' \; \
  rename-session 'cs5131-project' \; \
  detach-client
