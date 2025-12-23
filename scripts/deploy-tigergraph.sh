#!/bin/bash

# TigerGraph K8s 部署脚本

echo "开始部署 TigerGraph 到 K8s 集群..."

# 创建命名空间
kubectl apply -f deployments/tigergraph-k8s.yaml

echo "等待 TigerGraph Pod 启动..."
kubectl wait --for=condition=ready pod -l app=tigergraph -n tigergraph --timeout=300s

# 获取服务信息
REST_PORT=$(kubectl get service tigergraph-rest -n tigergraph -o jsonpath='{.spec.ports[0].nodePort}')
GUI_PORT=$(kubectl get service tigergraph-gui -n tigergraph -o jsonpath='{.spec.ports[0].nodePort}')

echo "TigerGraph 部署完成！"
echo "REST API: http://localhost:$REST_PORT"
echo "GUI: http://localhost:$GUI_PORT"

# 初始化图数据库
echo "初始化图数据库..."
sleep 30

# 获取 Pod 名称
POD_NAME=$(kubectl get pods -n tigergraph -l app=tigergraph -o jsonpath='{.items[0].metadata.name}')

# 在 TigerGraph Pod 中执行初始化命令
kubectl exec -it $POD_NAME -n tigergraph -- bash -c "
gsql -e 'CREATE VERTEX K8sNode (PRIMARY_ID id STRING, name STRING, labels STRING, status STRING)'
gsql -e 'CREATE VERTEX Pod (PRIMARY_ID id STRING, name STRING, namespace STRING, status STRING, node STRING)'
gsql -e 'CREATE VERTEX Service (PRIMARY_ID id STRING, name STRING, namespace STRING, type STRING, clusterIP STRING)'
gsql -e 'CREATE VERTEX Deployment (PRIMARY_ID id STRING, name STRING, namespace STRING, replicas INT32)'
gsql -e 'CREATE VERTEX ConfigMap (PRIMARY_ID id STRING, name STRING, namespace STRING)'
gsql -e 'CREATE VERTEX Secret (PRIMARY_ID id STRING, name STRING, namespace STRING, type STRING)'
gsql -e 'CREATE VERTEX Namespace (PRIMARY_ID id STRING, name STRING, status STRING)'
gsql -e 'CREATE VERTEX RBAC (PRIMARY_ID id STRING, type STRING, rules STRING)'
gsql -e 'CREATE VERTEX Container (PRIMARY_ID id STRING, name STRING, image STRING, ports STRING)'
gsql -e 'CREATE UNDIRECTED EDGE runs_on (FROM Pod, TO K8sNode)'
gsql -e 'CREATE UNDIRECTED EDGE exposes (FROM Service, TO Pod)'
gsql -e 'CREATE UNDIRECTED EDGE manages (FROM Deployment, TO Pod)'
gsql -e 'CREATE UNDIRECTED EDGE uses_config (FROM Pod, TO ConfigMap)'
gsql -e 'CREATE UNDIRECTED EDGE uses_secret (FROM Pod, TO Secret)'
gsql -e 'CREATE UNDIRECTED EDGE contains (FROM Namespace, TO Pod)'
gsql -e 'CREATE UNDIRECTED EDGE has_permission (FROM RBAC, TO Pod)'
gsql -e 'CREATE UNDIRECTED EDGE has_container (FROM Pod, TO Container)'
gsql -e 'CREATE GRAPH K8sSecurityGraph(K8sNode, Pod, Service, Deployment, ConfigMap, Secret, Namespace, RBAC, Container, runs_on, exposes, manages, uses_config, uses_secret, contains, has_permission, has_container)'
gsql -e 'USE GRAPH K8sSecurityGraph'
"

echo "TigerGraph 初始化完成！"