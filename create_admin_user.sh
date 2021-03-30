#!/bin/bash
# Usage create_admin_user.sh -u user -p password -h host -k private_key
#
# Description of required command line arguments:
#
#   -u: admin user name
#   -p: admin user password
#   -h: host name or IP address
#   -k: path to private SSH key file
#
# Usage example: create_admin_user.sh -u xrd -p secret -h host -k private_key_file

usage() {
  echo "Usage: create_admin_user.sh -u xrd -p secret -h host -k private_key_file"
}

exit_abnormal() {
  usage
  exit 1
}

create_user() {
    user=$1
    pass=$2
    host=$3
    ssh_key=$4
    ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR -i $ssh_key root@$host "adduser $user --group sudo -p $pass"
}

while getopts ":u:p:h:k:" options; do
  case "${options}" in
    u )
      USER=${OPTARG}
      ;;
    p )
      PASS=${OPTARG}
      ;;
    h )
      HOST=${OPTARG}
      ;;
    k )
      KEY=${OPTARG}
      ;;
    \? )
        exit_abnormal
      ;;
  esac
done

if [[ $USER == "" ]] | [[ $PASS == "" ]] | [[ $HOST == "" ]] | [[ $KEY == "" ]]; then
    exit_abnormal
fi

create_user "$USER" "$PASS" "$HOST" "$KEY"
