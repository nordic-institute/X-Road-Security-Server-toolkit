#!/bin/bash
# Usage run_end_to_end_tests.sh -c config_file
#                               -a configuration_anchor
#                               -h security_server_host
#                               -n security_server_name
#                               -k private_key_file_env_var
#                               -s ssh_user_env_var
#                               -u credentials_env_var
#                               -b api_key_env_var
#
# Description of required command line arguments:
#
#   -c: config file
#   -a: configuration-anchor file
#   -h: host name or IP address of the security server
#   -n: security server name
#   -k: private ssh key file environment variable
#   -s: ssh_user environment variable
#   -u: credentials environment variable
#   -b: api-key environment variable
#
#
# Usage example: run_end_to_end_tests.sh -c tests/resources/test-config-template.yaml
#                                        -a /etc/xroad/configuration_anchor.xml
#                                        -h ss
#                                        -n ss
#                                        -k TOOLKIT_SSH_PRIVATE_KEY
#                                        -s TOOLKIT_SSH_USER
#                                        -u TOOLKIT_ADMIN_CREDENTIALS
#                                        -b TOOLKIT_API_KEY

OUTPUT="tests/resources/test-config.yaml"

usage() {
  echo "Usage: run_end_to_end_tests.sh -c config_file
                                           -a configuration_anchor
                                           -h security_server_host
                                           -n security_server_name
                                           -k private_key_file_env_var
                                           -s ssh_user_env_var
                                           -u credentials_env_var
                                           -b api_key_env_var"
}

exit_abnormal() {
  usage
  exit 1
}

update_config() {
  local cmd
  cmd=""

  ssn=0
  api_keys=$(echo "$9" | tr "," "\n")
  for api_key in $api_keys
  do
    cmd="${cmd}.security_server[$ssn].api_key=\"$api_key\"|"
    ((ssn=ssn+1))
  done

  ssn=0
  names=$(echo "$4" | tr "," "\n")
  for name in $names
  do
    cmd="${cmd}.security_server[$ssn].ssh_private_key=\"$5\"|"
    cmd="${cmd}.security_server[$ssn].admin_credentials=\"$6\"|"
    cmd="${cmd}.security_server[$ssn].ssh_user=\"$8\"|"
    cmd="${cmd}.security_server[$ssn].configuration_anchor=\"$2\"|"
    cmd="${cmd}.security_server[$ssn].name=\"$name\"|"
    cmd="${cmd}.security_server[$ssn].security_server_code=\"$name\"|"
    ((ssn=ssn+1))
  done

  ssn=0
  hosts=$(echo "$3" | tr "," "\n")
  for host in $hosts
  do
    if [[ $ssn == 0 ]]; then
      cmd="${cmd}.security_server[$ssn].url=\"https://$host:4000/api/v1\"|"
    else
      cmd="${cmd}.security_server[$ssn].url=\"https://$host:4000/api/v1\""
    fi
    ((ssn=ssn+1))
  done

  yq -y "$cmd" "$1" > "$7"
  chmod 777 "$7"
}

run_tests() {
  python -m pytest -v tests/end_to_end/tests.py -c "$1"
}

while getopts ":c:a:h:n:k:s:u:b:" options; do
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
      KEY_ENV=${OPTARG}
      ;;
    s )
      SSH_USER_ENV=${OPTARG}
      ;;
    u )
      CREDENTIALS_ENV=${OPTARG}
      ;;
    b )
      API_KEY_ENV=${OPTARG}
      ;;      
    \? )
        exit_abnormal
      ;;
  esac
done

if [[ $CONFIG == "" ]] | [[ $ANCHOR == "" ]] | [[ $HOST == "" ]] | \
   [[ $NAME == "" ]] | [[ $KEY_ENV == "" ]] | [[ $SSH_USER_ENV == "" ]] | [[ $CREDENTIALS_ENV == "" ]] | [[ $API_KEY_ENV == "" ]]; then
    exit_abnormal
fi

update_config "$CONFIG" "$ANCHOR" "$HOST" "$NAME" "$KEY_ENV" "$CREDENTIALS_ENV" "$OUTPUT" "$SSH_USER_ENV" "$API_KEY_ENV"
run_tests "$OUTPUT"
