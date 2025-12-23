# TigerGraph Docker 部署指南

## 快速启动 TigerGraph

你已经正确运行了 TigerGraph Docker 容器：

```bash
docker run -d -p 14022:22 -p 9000:9000 -p 14240:14240 \
  --name tigergraph \
  --ulimit nofile=1000000:1000000 \
  -v ~/TigerGraph/data:/home/tigergraph/mydata \
  -v tg-data:/home/tigergraph \
  -t tigergraph/tigergraph:latest
```

## 是否需要进入容器？

**是的，需要进入容器初始化图数据库结构！**

### 方法1：使用初始化脚本（推荐）
```bash
cd scripts
chmod +x init-tigergraph-docker.sh
./init-tigergraph-docker.sh
```

### 方法2：手动进入容器
```bash
# 进入容器
docker exec -it tigergraph bash

# 在容器内执行
gsql
```

在 gsql 命令行中执行以下命令：

```sql
-- 创建顶点类型
CREATE VERTEX K8sNode (PRIMARY_ID id STRING, name STRING, labels STRING, status STRING);
CREATE VERTEX Pod (PRIMARY_ID id STRING, name STRING, namespace STRING, status STRING, node STRING);
CREATE VERTEX Service (PRIMARY_ID id STRING, name STRING, namespace STRING, type STRING, clusterIP STRING);
CREATE VERTEX Deployment (PRIMARY_ID id STRING, name STRING, namespace STRING, replicas INT32);
CREATE VERTEX ConfigMap (PRIMARY_ID id STRING, name STRING, namespace STRING);
CREATE VERTEX Secret (PRIMARY_ID id STRING, name STRING, namespace STRING, type STRING);
CREATE VERTEX Namespace (PRIMARY_ID id STRING, name STRING, status STRING);
CREATE VERTEX RBAC (PRIMARY_ID id STRING, type STRING, rules STRING);
CREATE VERTEX Container (PRIMARY_ID id STRING, name STRING, image STRING, ports STRING);

-- 创建边类型
CREATE UNDIRECTED EDGE runs_on (FROM Pod, TO K8sNode);
CREATE UNDIRECTED EDGE exposes (FROM Service, TO Pod);
CREATE UNDIRECTED EDGE manages (FROM Deployment, TO Pod);
CREATE UNDIRECTED EDGE uses_config (FROM Pod, TO ConfigMap);
CREATE UNDIRECTED EDGE uses_secret (FROM Pod, TO Secret);
CREATE UNDIRECTED EDGE contains (FROM Namespace, TO Pod);
CREATE UNDIRECTED EDGE has_permission (FROM RBAC, TO Pod);
CREATE UNDIRECTED EDGE has_container (FROM Pod, TO Container);

-- 创建图
CREATE GRAPH K8sSecurityGraph(K8sNode, Pod, Service, Deployment, ConfigMap, Secret, Namespace, RBAC, Container, runs_on, exposes, manages, uses_config, uses_secret, contains, has_permission, has_container);

-- 使用图
USE GRAPH K8sSecurityGraph;
```

## 启动后端服务

初始化完成后，在新的终端中：

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

## 启动前端服务

```bash
cd frontend
npm install
npm start
```

## 访问地址

- **TigerGraph GUI**: http://localhost:14240
- **TigerGraph REST API**: http://localhost:9000
- **后端 API**: http://localhost:8000
- **前端界面**: http://localhost:3000

## 验证连接

1. 访问 http://localhost:14240 确认 TigerGraph GUI 正常
2. 访问 http://localhost:8000/health 检查后端连接状态
3. 在前端界面中进行资产发现和导入