#!/bin/bash
# Usage run_end_to_end_tests.sh -c config_file -a configuration_anchor -h security_server_host -n security_server_name -k private_key_file
#
# Description of required command line arguments:
#
#   -c: config file
#   -a: configuration-anchor file
#   -h: host name or IP address of the security server
#   -n: security server name
#   -k: private ssh key file
#
#
# Usage example: run_end_to_end_tests.sh -c tests/resources/test-config.yaml -a /etc/xroad/configuration_anchor.xml -h ss -n ss -k /home/user/id_rsa


usage() {
  echo "Usage: run_end_to_end_tests.sh -c config_file -a configuration_anchor -h security_server_host -n security_server_name -k private_key_file"
}

exit_abnormal() {
  usage
  exit 1
}

update_config() {
  cmd=".api_key[0].key=\"$5\""
  cmd="${cmd}|.security_server[0].configuration_anchor=\"$2\""
  cmd="${cmd}|.security_server[0].name=\"$4\""
  cmd="${cmd}|.security_server[0].security_server_code=\"$4\""
  cmd="${cmd}|.security_server[0].url=\"https://$3:4000/api/v1\""
  yq -y "$cmd" "$1" > tests/resources/test-config.yaml
  chmod 777 tests/resources/test-config.yaml
}

init() {
  source env/bin/activate
  response=${"xrdsst -c tests/resources/test-config.yaml init status"}
  echo "response: \n $response"
  rm tests/resources/test-config.yaml
}


while getopts ":c:a:h:n:k:" options; do
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
    \? )
        exit_abnormal
      ;;
  esac
done

if [[ $CONFIG == "" ]] | [[ $ANCHOR == "" ]] | [[ $HOST == "" ]] | [[ $NAME == "" ]] | [[ $KEY == "" ]]; then
    exit_abnormal
fi

update_config "$CONFIG" "$ANCHOR" "$HOST" "$NAME" "$KEY"
init