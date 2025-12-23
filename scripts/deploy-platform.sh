#!/bin/bash

echo "部署 K8s Native Security Platform..."

# 检查依赖
echo "检查依赖..."
if ! command -v docker &> /dev/null; then
    echo "错误: Docker 未安装"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "错误: Docker Compose 未安装"
    exit 1
fi

if ! command -v kubectl &> /dev/null; then
    echo "错误: kubectl 未安装"
    exit 1
fi

# 构建并启动服务
echo "构建并启动服务..."
docker-compose up --build -d

# 等待服务启动
echo "等待服务启动..."
sleep 30

# 检查服务状态
echo "检查服务状态..."
docker-compose ps

# 获取 TigerGraph Pod 信息
echo ""
echo "服务已启动！"
echo "前端地址: http://localhost:3000"
echo "后端 API: http://localhost:8000"
echo "TigerGraph GUI: http://localhost:14240"
echo ""
echo "首次使用请："
echo "1. 访问前端界面"
echo "2. 在'资产发现'页面点击'发现资产'"
echo "3. 点击'导入 TigerGraph'"
echo "4. 在'图谱可视化'页面查看资产关系图"