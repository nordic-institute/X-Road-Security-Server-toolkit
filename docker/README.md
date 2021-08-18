
# Dockerized X-Road-Security-Server-toolkit

With these tools one doesn't have to install python to local machine in order to use toolkit. 

Note that:
- this Dockerfile clones toolkit with tag v3.0 statically
- ssh keys are generated in docker build phase to /usr/src/ssh -folder

### Setup

[Normal requirements for a toolkit apply](https://github.com/nordic-institute/X-Road-Security-Server-toolkit/blob/master/docs/xroad_security_server_toolkit_user_guide.md#3-configuration-of-x-road-security-server)

- docker-compose - configured docker network must provide access from toolkit container to ss1. This docker compose introduces xroad-network named bridge network.
- configuration-anchor - introduce configuration anchor from your central server to this folder in order for it to be mounted to the toolkit container
- configuration.yml - introduce your configuration file to this folder in order for it to be mounted to the toolkit container

### Usage

```
docker-compose build
docker-compose run --rm toolkit
source ./toolkit/env/bin/activate
```


