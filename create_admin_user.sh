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
    os_name=$(ssh -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR -i "$ssh_key" root@"$host" "grep '^NAME' /etc/os-release")

    if echo "$os_name" | grep 'Ubuntu'; then
      ssh -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR -i "$ssh_key" root@"$host" "adduser $user --group sudo -p $pass"
    fi
    if echo "$os_name" | grep 'Centos'; then
      ssh -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR -i "$ssh_key" root@"$host" "useradd --system --home /var/lib/xroad --no-create-home --shell /bin/bash --user-group --comment \"X-Road system user\" xroad"
      ssh -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR -i "$ssh_key" root@"$host" "mkdir /etc/xroad"
      ssh -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR -i "$ssh_key" root@"$host" "chown xroad:xroad /etc/xroad"
      ssh -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR -i "$ssh_key" root@"$host" "chmod 751 /etc/xroad"
      ssh -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR -i "$ssh_key" root@"$host" "touch /etc/xroad/db.properties"
      ssh -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR -i "$ssh_key" root@"$host" "chown xroad:xroad /etc/xroad/db.properties"
      ssh -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR -i "$ssh_key" root@"$host" "chmod 640 /etc/xroad/db.properties"
      ssh -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR -i "$ssh_key" root@"$host" "adduser $user --group sudo -p $pass"
    fi
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
