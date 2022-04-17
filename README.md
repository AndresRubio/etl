# Intro

This projects aims to create a local cloud env for testing with python with some etl steps given an input.
It is also useful to install awslocal but not mandatory `pip3 install awslocal`

## How to run 
In case you installed awslocal if not can skip this part
- To configure a proper credentials for aws local you need to install aws cli 
  `curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
  unzip awscliv2.zip
  sudo ./aws/install`
- after that execute `aws configure --profile localstack`
- AWS Access Key ID [None]: test
- AWS Secret Access Key [None]: test
- Default region name [None]: eu-central-1
- Default output format [None]:

1. Sets Pyenv or pipfile to python version 3.8.8 to execute in local mode
2. Creates env for test ```docker run --rm -it -p 4566:4566 -p 4571:4571 localstack/localstack:0.13.1 -e "SERVICES=s3" -d ```
3. ```python3 -m unnittest discover . -p "test_* -s "./test/unit""```  or from your id execute launcher.py

## Dockerize
Only to show a dockerization process execute tests to run app
```docker build -t next/web-app -f dockerfiles/Dockerfile . ```
```docker build -t next/web-app .```

# Extra in beta
This part tries to create an orchestrator based in k8s where you can deploy all the artifacts **not completed**
Manual web-app installation on minikube cluster from local, not for prod!!!

Add local docker registry to be read by minikube
- ```eval $(minikube -p minikube docker-env)```
- ```kubectl apply -f k8s/web-app/deployment.yaml ```
- ```kubectl apply -f k8s/web-app/service.yaml ```
- ```minikube ip``` to get cluster ip
- ```kubectl apply -f k8s/localstack/deployment.yaml ```
- ```kubectl apply -f k8s/localstack/service.yaml ```
- To expose localstack services ```kubectl expose pod -n localstack localstack-5d4bb7c995-p97jk --type=LoadBalancer --port=4566 --target-port=4566```
- Access via ```http://cluster-ip:nodeport```