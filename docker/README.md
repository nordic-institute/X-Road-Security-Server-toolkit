
# Dockerized X-Road-Security-Server-toolkit

With these tools one doesn't have to install python to local machine in order to use toolkit. 

Note that:
- this Dockerfile clones toolkit with tag v2.0 statically
- ssh keys are generated in docker build phase to /usr/src/ssh -folder

### Setup to configure a central server

Normal requirements for a toolkit apply:
- Central server and configured security server with management services are required

- docker-compose - configured docker network must provide access from toolkit container to ss1. This docker compose introduces xroad-network named bridge network.
- configuration-anchor - introduce configuration anchor from your setups central server
- configuration.yml - introduce your configuration file to this folder in order for it to mounted to the toolkit container

### Usage

```
docker-compose build
docker-compose run --rm toolkit
source ./toolkit/env/bin/activate
```


