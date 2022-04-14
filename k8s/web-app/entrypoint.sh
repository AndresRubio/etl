#!/bin/bash

echo "Waiting 20 seconds"
sleep 20

echo "Create .kube folder"
mkdir -p $HOME/.kube

echo "Copy kubeconfig.yaml file"
sed "s/127.0.0.1/k3s-server/g;" /output/kubeconfig.yaml > $HOME/.kube/config

echo "Create web-app namespace"
kubectl create namespace web-app

echo "Installing web-app"
kubectl -n web-app apply -f deployment.yaml
kubectl -n web-app apply -f service.yaml
