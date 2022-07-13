#!/bin/bash

DEBUG=${DEBUG:-"false"}
BACKUP_DIR=${BACKUP_DIR:-/backups}
BACKUP_ROTATE=${BACKUP_ROTATE:-7}
AWSCLI_CREDS=${AWSCLI_CREDS:-"$HOME/.aws/credentials"}
S3_ENDPOINT=${S3_ENDPOINT:-"https://s3.amazonaws.com"}
S3_BUCKET_URI=${S3_BUCKET_URI:-""}

[[ "${DEBUG}" =~ (1|true) ]] && set -x


function backup_openstack_apis() {
  echo ">>> Backing up OpenStack servers"
  timestamp=$(date +%Y%m%d%H%M%S)
}


function retention() {
  backups_to_delete=$(find "${BACKUP_DIR}" -type f | sort -rn | tail -n +$((${BACKUP_ROTATE} + 1)))
  echo ">>> Running retention (rotate: ${BACKUP_ROTATE})"
  for f in $backups_to_delete; do
    echo "removing ${f}"
    rm -f "${f}"
  done
}

function sync_s3_to_backups_dir() {
  echo ">>> Syncing ${S3_BUCKET_URI} to ${BACKUP_DIR} (endpoint: ${S3_ENDPOINT})"
  aws --endpoint-url "${S3_ENDPOINT}" s3 sync "${S3_BUCKET_URI}" "${BACKUP_DIR}"
}

function sync_backups_to_s3() {
  echo ">>> Syncing OpenStack API backups to ${S3_BUCKET_URI} (endpoint: ${S3_ENDPOINT})"
  aws --endpoint-url "${S3_ENDPOINT}" s3 sync --delete "${BACKUP_DIR}" "${S3_BUCKET_URI}"
}


function exit_error() {
  echo $1 1>&2
  exit 1
}


function validate_input() {
  if [ ! -d "${BACKUP_DIR}" ]; then
    exit_error "BACKUP_DIR does not exist: ${BACKUP_DIR}"
  fi
  if [ ! -f "${AWSCLI_CREDS}" ]; then
    exit_error "AWSCLI_CREDS does not exist: ${AWSCLI_CREDS}"
  fi
}


function main() {
  sync_s3_to_backups_dir
  validate_input
  backup_servers
  retention
  sync_backups_to_s3
}

main
