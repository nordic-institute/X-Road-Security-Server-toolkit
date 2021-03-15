#!/bin/bash
# Usage reset_security_server.sh -n server(s) -h path/to/hosts.txt -a path/to/ansible -u ssh_user -k path/to/public_key_file
#
# Description of required command line arguments:
#
#   -n: name(s) of security servers to be re-initialized (has to conform with the ones listed in hosts file)
#   -h: lxd hosts file, this file is used by the Ansible script to install security servers
#   -a: path to ansible script, this is the path to where the Ansible script is located in the locally cloned X-Road Git repository
#   -u: ssh user name
#   -k: path to public ssh key file
#
#   The LXD hosts file and the Ansible script file that should be used by this script can be found here:
#   https://github.com/nordic-institute/X-Road/blob/develop/ansible
#
# Usage example: reset_security_server.sh -n ss3,ss4 -h ../X-Road/ansible/hosts/lxd_hosts.txt -a ../X-Road/ansible -u ssh_user -k public_key_file

ANSIBLE_CMD="ansible-playbook"
ANSIBLE_SCRIPT="xroad_init.yml"
SSH_FOLDER=".ssh"
AUTHORIZED_KEYS_FILE="authorized_keys"

usage() {
  echo "Usage: reset_security_server.sh -n name(s) -h hosts.txt -a ansible_folder -u ssh_user -k public_key_file"
}

exit_abnormal() {
  usage
  exit 1
}

delete_containers() {
names=$(echo "$1" | tr "," "\n")
container_list=$(lxc list --format=json | jq -r '.[] | .name + ","')
containers=$(echo "$container_list" | tr "," "\n")
for name in $names
do
    for container in $containers
    do
        if [ "$name" = "$container" ]
        then
            printf "\n Deleting LXD container %s\n" "$name"
            lxc delete "$name" -f
        fi
    done
done
}

run_ansible_script() {
    if [ ! -d "$1" ]; then
        printf "\n The directory %s does not exist" "$1"
        exit 1
    fi
    if [[ -f "$1/$4" ]]; then
        printf "\nRunning %s -i %s %s\n" "$2" "$3" "$1/$4"
        "$2" -i "$3" "$1/$4"
        printf "\n Ansible script finished installing security servers \n"
    else
        printf "\n The file %s does not exist" "$1/$4"
        exit 1
    fi
}

add_public_key() {
    names=$(echo "$1" | tr "," "\n")
    for name in $names
    do
        printf "\nAdding public key to LXD container %s\n" "$name"
        lxc exec "$name" -- bash -c "useradd -c \"$2 user\" -d /home/$2 -s /bin/bash $2"
        lxc exec "$name" -- bash -c "echo \"$2 ALL=(ALL) NOPASSWD: ALL\" > /etc/sudoers.d/$2"
        lxc exec "$name" -- bash -c "mkdir -p /home/$2/$4"
        lxc exec "$name" -- bash -c "echo \"$(cat "$3")\" > /home/$2/$4/$5"
        lxc exec "$name" -- bash -c "chown -R $2:$2 /home/$2"
        lxc exec "$name" -- bash -c "chmod 0700 /home/$2"
        lxc exec "$name" -- bash -c "chmod 0700 /home/$2/$4"
        lxc exec "$name" -- bash -c "chmod 0600 /home/$2/$4/$5"
    done
}

while getopts ":n:h:a:u:k:" options; do
  case "${options}" in
    n )
      NAME=${OPTARG}
      ;;
    h )
      HOSTS=${OPTARG}
      ;;
    a )
      ANSIBLE=${OPTARG}
      ;;
    u )
      USER=${OPTARG}
      ;;
    k )
      KEY=${OPTARG}
      ;;
    \? )
        exit_abnormal
      ;;
  esac
done


if [[ $NAME == "" ]] | [[ $HOSTS == "" ]] | [[ $ANSIBLE == "" ]] | [[ $USER == "" ]] | [[ $KEY == "" ]]; then
    exit_abnormal
fi

delete_containers "$NAME"
run_ansible_script "$ANSIBLE" "$ANSIBLE_CMD" "$HOSTS" "$ANSIBLE_SCRIPT"
add_public_key "$NAME" "$USER" "$KEY" "$SSH_FOLDER" "$AUTHORIZED_KEYS_FILE"






