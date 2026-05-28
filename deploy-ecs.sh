#!/bin/bash
# ECS 部署脚本
# 使用: scp 此脚本到服务器后执行，或直接运行此脚本（需配置 SSH）

set -e

SERVER="root@8.137.103.202"
DEPLOY_DIR="/var/www/ai-chat"
COMPOSE_FILE="docker-compose.prod.yml"

echo "🚀 开始部署 AI Chat 到 $SERVER ..."

# 1. 在服务器上创建目录
ssh $SERVER "mkdir -p $DEPLOY_DIR/uploads $DEPLOY_DIR/data/chroma $DEPLOY_DIR/backend $DEPLOY_DIR/frontend"

# 2. 上传 docker-compose 文件
echo "📦 上传 Docker Compose 配置..."
scp $COMPOSE_FILE $SERVER:$DEPLOY_DIR/
scp backend/.env.prod $SERVER:$DEPLOY_DIR/backend/.env

# 3. 上传前端构建产物
echo "📦 上传前端构建文件..."
cd frontend/dist && tar czf /tmp/frontend-dist.tar.gz .
cd -
scp /tmp/frontend-dist.tar.gz $SERVER:$DEPLOY_DIR/frontend-dist.tar.gz
ssh $SERVER "cd $DEPLOY_DIR && mkdir -p frontend/dist && cd frontend && tar xzf ../frontend-dist.tar.gz -C dist/"

# 4. 上传后端代码（排除本地虚拟环境等）
echo "📦 上传后端代码..."
cd backend && tar czf /tmp/backend-src.tar.gz \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.pytest_cache' \
  --exclude='.venv' \
  --exclude='venv' \
  app requirements.txt .env .env.prod Dockerfile
cd -
scp /tmp/backend-src.tar.gz $SERVER:$DEPLOY_DIR/backend-src.tar.gz
ssh $SERVER "cd $DEPLOY_DIR/backend && tar xzf ../backend-src.tar.gz"

# 5. 在服务器上启动服务
echo "🚀 启动服务..."
ssh $SERVER "cd $DEPLOY_DIR && docker compose -f $COMPOSE_FILE build && docker compose -f $COMPOSE_FILE up -d"

# 6. 检查服务状态
echo "✅ 检查服务状态..."
ssh $SERVER "cd $DEPLOY_DIR && docker compose -f $COMPOSE_FILE ps"

echo ""
echo "🎉 部署完成！"
echo "前端: http://8.137.103.202"
echo "后端 API: http://8.137.103.202:8000"
echo "API 文档: http://8.137.103.202:8000/docs"
