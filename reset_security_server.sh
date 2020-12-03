#!/bin/bash
# Usage reset_security_server.sh -n server(s) -h path/to/hosts.txt -a path/to/ansible
#
# Description of required command line arguments:
#
#   -n: name(s) of security servers to be re-initialized (has to conform with the ones listed in hosts file)
#   -h: lxd hosts file, this file is used by the Ansible script to install security servers
#   -a: path to ansible script, this is the path to where the Ansible script is located in the locally cloned X-Road Git repository
#
#   The LXD hosts file and the Ansible script file that should be used by this script can be found here:
#   https://github.com/nordic-institute/X-Road/blob/develop/ansible
#
# Usage example: reset_security_server.sh -n ss3,ss4 -h ../X-Road/ansible/hosts/lxd_hosts.txt -a ../X-Road/ansible

ANSIBLE_CMD="ansible-playbook"
ANSIBLE_SCRIPT="xroad_init.yml"
URL=https://localhost:4000/api/v1/api-keys
ROLES='["XROAD_SYSTEM_ADMINISTRATOR","XROAD_SECURITY_OFFICER"]'
HEADER='Content-Type: application/json'

usage() {
  echo "Usage: reset_security_server.sh -n name(s) -h hosts.txt -a ansible_folder"
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

create_api_keys() {
    names=$(echo "$1" | tr "," "\n")
    for name in $names
    do
        printf "\nCreating api-key for LXD container %s\n" "$name"
        FILE=api-key-$name.txt
        lxc exec "$name" -- curl -X POST -u xrd:secret --retry 30 --retry-connrefused --silent "$2" --data "$3" --header "$4" -k -o "$FILE"
        lxc exec "$name" -- cat api-key-"$name".txt | jq '.key'
        printf "\n"
    done
}

while getopts ":n:h:a:" options; do
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
    \? )
        exit_abnormal
      ;;
  esac
done


if [[ $NAME == "" ]] | [[ $HOSTS == "" ]] | [[ $ANSIBLE == "" ]]; then
    exit_abnormal
fi

delete_containers "$NAME"
run_ansible_script "$ANSIBLE" "$ANSIBLE_CMD" "$HOSTS" "$ANSIBLE_SCRIPT"
create_api_keys "$NAME" "$URL" "$ROLES" "$HEADER"






