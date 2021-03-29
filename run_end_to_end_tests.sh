#!/bin/bash
# Usage run_end_to_end_tests.sh -c config_file
#                               -a configuration_anchor
#                               -h security_server_host
#                               -n security_server_name
#                               -k private_key_file
#                               -s ssh_user
#                               -u credentials
#
# Description of required command line arguments:
#
#   -c: config file
#   -a: configuration-anchor file
#   -h: host name or IP address of the security server
#   -n: security server name
#   -k: private ssh key file
#   -s: ssh_user
#   -u: credentials
#
#
# Usage example: run_end_to_end_tests.sh -c tests/resources/test-config-template.yaml
#                                        -a /etc/xroad/configuration_anchor.xml
#                                        -h ss
#                                        -n ss
#                                        -k /home/user/id_rsa
#                                        -s ssh_user
#                                        -u xrd:secret

OUTPUT="tests/resources/test-config.yaml"

usage() {
  echo "Usage: run_end_to_end_tests.sh -c config_file
                                           -a configuration_anchor
                                           -h security_server_host
                                           -n security_server_name
                                           -k private_key_file
                                           -s ssh_user
                                           -u credentials"
}

exit_abnormal() {
  usage
  exit 1
}

update_config() {
  local cmd
  cmd=""
  cmd=".security_server[0].api_key[0].ssh_key=\"$5\""
  cmd="${cmd}|.security_server[0].api_key[0].credentials=\"$6\""
  cmd="${cmd}|.security_server[0].api_key[0].ssh_user=\"$8\""
  cmd="${cmd}|.security_server[0].configuration_anchor=\"$2\""
  cmd="${cmd}|.security_server[0].name=\"$4\""
  cmd="${cmd}|.security_server[0].security_server_code=\"$4\""
  cmd="${cmd}|.security_server[0].url=\"https://$3:4000/api/v1\""
  yq -y "$cmd" "$1" > "$7"
  chmod 777 "$7"
}

run_tests() {
  python -m pytest -v tests/end_to_end/tests.py -c "$1"
}

while getopts ":c:a:h:n:k:s:u:" options; do
  case "${options}" in
    c )
      CONFIG=${OPTARG}
      ;;
    a )
      ANCHOR=${OPTARG}
      ;;
    h )
      HOST=${OPTARG}
      ;;
    n )
      NAME=${OPTARG}
      ;;
    k )
      KEY=${OPTARG}
      ;;
    s )
      SSH_USER=${OPTARG}
      ;;
    u )
      CREDENTIALS=${OPTARG}
      ;;
    \? )
        exit_abnormal
      ;;
  esac
done

if [[ $CONFIG == "" ]] | [[ $ANCHOR == "" ]] | [[ $HOST == "" ]] | \
   [[ $NAME == "" ]] | [[ $KEY == "" ]] | [[ $SSH_USER == "" ]] | [[ $CREDENTIALS == "" ]]; then
    exit_abnormal
fi

update_config "$CONFIG" "$ANCHOR" "$HOST" "$NAME" "$KEY" "$CREDENTIALS" "$OUTPUT" "$SSH_USER"
run_tests "$OUTPUT"
