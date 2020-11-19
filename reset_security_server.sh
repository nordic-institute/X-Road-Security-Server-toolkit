#!/bin/bash
# Script should be run as sudo
# Usage reset_security_server.sh -n=server(s) -h=path/to/hosts.txt -a=path/to/ansible
# Usage example: reset_security_server.sh -n=ss3,ss4 -h=../../X-Road/ansible/hosts/lxd_hosts.txt -a=../../X-Road/ansible

if [ "$#" -ne 3 ]; then
    echo "Usage: reset_security_server.sh -n=name(s) -h=hosts.txt -a=ansible_folder"
    exit 1
fi

for i in "$@"
do
case $i in
    -n=*|--name=*)
    NAME="${i#*=}"
    shift
    ;;
    -h=*|--hosts=*)
    HOSTS="${i#*=}"
    shift
    ;;
    -a=*|--ansible=*)
    ANSIBLE="${i#*=}"
    shift
    ;;
    *)
        echo "Usage: reset_security_server.sh -n=name(s) -h=hosts.txt -a=ansible_folder"
        exit 1
    ;;
esac
done

names=$(echo "$NAME" | tr "," "\n")
container_list=$(lxc list --format=json | jq -r '.[] | .name + ","')
containers=$(echo "$container_list" | tr "," "\n")

for name in $names
do
    for container in $containers
    do
        if [ $name = $container ]
        then
            printf "\n Deleting LXD container %s\n" "$name"
            lxc delete "$name" -f
        fi
    done
done

cd $ANSIBLE
printf "\nRunning Ansible script: %s/ansible-playbook -i %s xroad_init.yml\n" "$ANSIBLE" "$HOSTS"
ansible-playbook -i "$HOSTS" xroad_init.yml

printf "\n Ansible script finished installing security servers \n"

URL=https://localhost:4000/api/v1/api-keys
ROLES='["XROAD_SYSTEM_ADMINISTRATOR"]'
HEADER='Content-Type: application/json'

for name in $names
do
    printf "\nCreating api-key for LXD container %s\n" "$name"
    FILE=api-key-$name.txt
    lxc exec "$name" -- sudo curl -X POST -u xrd:secret --retry 30 --retry-connrefused --silent $URL --data "$ROLES" --header "$HEADER" -k -o "$FILE"
    lxc exec "$name" -- cat api-key-"$name".txt | jq '.key'
    printf "\n"
done






