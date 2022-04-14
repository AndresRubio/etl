#!/bin/bash

echo "Waiting 20 seconds"
sleep 20

echo "Create .kube folder"
mkdir -p $HOME/.kube

echo "Copy kubeconfig.yaml file"
sed "s/127.0.0.1/k3s-server/g;" /output/kubeconfig.yaml > $HOME/.kube/config

echo "Create localstack namespace"
kubectl create namespace localstack

echo "Installing localstack"
kubectl -n localstack apply -f deployment.yaml
kubectl -n localstack apply -f service.yaml

