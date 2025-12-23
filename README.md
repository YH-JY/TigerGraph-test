# K8s Native Security Platform

## 项目概述

这是一个用于发现 Kubernetes 集群资产并分析云原生攻击路径的安全平台。平台使用 TigerGraph 图数据库存储和分析云原生资产之间的关系，帮助识别潜在的安全风险。

## 功能特性

- **资产发现**: 自动发现 K8s 集群中的各种资源（Pod、Service、Deployment、ConfigMap、Secret等）
- **图谱可视化**: 使用 Cytoscape.js 可视化资产之间的关系
- **攻击路径分析**: 基于图数据库查询潜在攻击路径
- **风险评估**: 对发现的攻击路径进行风险等级评估

## 架构设计

### 后端 (Python FastAPI)
- K8s API 客户端用于资产发现
- TigerGraph Python 客户端用于图数据库操作
- RESTful API 提供 CRUD 操作

### 前端 (React + TypeScript)
- Ant Design UI 组件库
- Cytoscape.js 图谱可视化
- Axios HTTP 客户端

### 数据库 (TigerGraph)
- 存储 K8s 资产作为顶点
- 存储资源关系作为边
- 提供图查询和路径分析

## 快速开始

### 方式一：使用 Docker Compose

1. 克隆项目
```bash
git clone <repository-url>
cd k8s-native-security-platform
```

2. 启动服务
```bash
docker-compose up -d
```

3. 访问应用
- 前端: http://localhost:3000
- 后端 API: http://localhost:8000
- TigerGraph GUI: http://localhost:14240

### 方式二：本地部署

#### 1. 部署 TigerGraph 到 K8s 集群

```bash
cd scripts
./deploy-tigergraph.sh
```

#### 2. 启动后端服务

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

#### 3. 启动前端服务

```bash
cd frontend
npm install
npm start
```

## 使用说明

1. **资产发现**
   - 在"资产发现"页面点击"发现资产"按钮
   - 系统会扫描整个 K8s 集群，发现所有资源
   - 点击"导入 TigerGraph"将数据导入图数据库

2. **查看仪表板**
   - 查看系统连接状态和统计信息
   - 监控各种资产类型的数量

3. **攻击路径分析**
   - 选择源和目标资产类型
   - 查询潜在的攻击路径
   - 查看风险等级评估

4. **图谱可视化**
   - 查看完整的资产关系图谱
   - 支持多种布局方式
   - 可以隐藏/显示标签

## 安全注意事项

1. 确保 K8s 配置文件权限安全
2. TigerGraph 默认密码应修改
3. API 应在受信任的网络环境中运行
4. 敏感信息（如 Secret）应谨慎处理

## 开发指南

### 环境变量配置

后端配置文件 `.env`:
```
TIGERGRAPH_HOST=localhost
TIGERGRAPH_PORT=9000
TIGERGRAPH_USERNAME=tigergraph
TIGERGRAPH_PASSWORD=tigergraph
TIGERGRAPH_GRAPH_NAME=K8sSecurityGraph

K8S_CONFIG_FILE=
K8S_IN_CLUSTER=false

API_HOST=0.0.0.0
API_PORT=8000
```

### API 文档

启动后端服务后，访问 http://localhost:8000/docs 查看 Swagger 文档。

## 故障排除

1. **K8s 连接失败**
   - 检查 kubeconfig 文件路径
   - 验证集群访问权限

2. **TigerGraph 连接失败**
   - 检查服务是否正常运行
   - 验证连接配置

3. **前端无法访问后端**
   - 检查 CORS 配置
   - 验证代理设置

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 发起 Pull Request

## 许可证

MIT License