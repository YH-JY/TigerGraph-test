#!/bin/bash

# TigerGraph Docker 容器初始化脚本
# 在 Docker 容器启动后执行此脚本来初始化图数据库

echo "开始初始化 TigerGraph 图数据库..."

# 等待 TigerGraph 服务启动
echo "等待 TigerGraph 服务启动..."
sleep 30

# 进入容器并执行初始化命令
docker exec -it tigergraph bash -c "
# 创建图数据库结构
echo '创建顶点类型...'
gsql -e 'CREATE VERTEX K8sNode (PRIMARY_ID id STRING, name STRING, labels STRING, status STRING)'
gsql -e 'CREATE VERTEX Pod (PRIMARY_ID id STRING, name STRING, namespace STRING, status STRING, node STRING)'
gsql -e 'CREATE VERTEX Service (PRIMARY_ID id STRING, name STRING, namespace STRING, type STRING, clusterIP STRING)'
gsql -e 'CREATE VERTEX Deployment (PRIMARY_ID id STRING, name STRING, namespace STRING, replicas INT32)'
gsql -e 'CREATE VERTEX ConfigMap (PRIMARY_ID id STRING, name STRING, namespace STRING)'
gsql -e 'CREATE VERTEX Secret (PRIMARY_ID id STRING, name STRING, namespace STRING, type STRING)'
gsql -e 'CREATE VERTEX Namespace (PRIMARY_ID id STRING, name STRING, status STRING)'
gsql -e 'CREATE VERTEX RBAC (PRIMARY_ID id STRING, type STRING, rules STRING)'
gsql -e 'CREATE VERTEX Container (PRIMARY_ID id STRING, name STRING, image STRING, ports STRING)'

echo '创建边类型...'
gsql -e 'CREATE UNDIRECTED EDGE runs_on (FROM Pod, TO K8sNode)'
gsql -e 'CREATE UNDIRECTED EDGE exposes (FROM Service, TO Pod)'
gsql -e 'CREATE UNDIRECTED EDGE manages (FROM Deployment, TO Pod)'
gsql -e 'CREATE UNDIRECTED EDGE uses_config (FROM Pod, TO ConfigMap)'
gsql -e 'CREATE UNDIRECTED EDGE uses_secret (FROM Pod, TO Secret)'
gsql -e 'CREATE UNDIRECTED EDGE contains (FROM Namespace, TO Pod)'
gsql -e 'CREATE UNDIRECTED EDGE has_permission (FROM RBAC, TO Pod)'
gsql -e 'CREATE UNDIRECTED EDGE has_container (FROM Pod, TO Container)'

echo '创建图...'
gsql -e 'CREATE GRAPH K8sSecurityGraph(K8sNode, Pod, Service, Deployment, ConfigMap, Secret, Namespace, RBAC, Container, runs_on, exposes, manages, uses_config, uses_secret, contains, has_permission, has_container)'

echo '切换到创建的图...'
gsql -e 'USE GRAPH K8sSecurityGraph'

echo 'TigerGraph 初始化完成！'
"

echo "TigerGraph 图数据库初始化脚本执行完成！"
echo ""
echo "现在你可以："
echo "1. 启动后端服务: cd backend && uvicorn main:app --reload"
echo "2. 访问前端: http://localhost:3000"
echo "3. 在前端界面中进行资产发现和导入"