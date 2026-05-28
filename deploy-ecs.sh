#!/bin/bash
# AI Chat Platform - ECS 部署脚本
# 在 ECS 服务器上运行此脚本

set -e

DEPLOY_DIR="/var/www/ai-chat"
REPO_URL="https://github.com/wesleycheng/ai-chat.git"
BRANCH="main"

echo "========================================="
echo " AI Chat Platform - ECS 部署"
echo "========================================="

# 1. 安装 Docker（如果未安装）
if ! command -v docker &> /dev/null; then
    echo "[1/6] 安装 Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
else
    echo "[1/6] Docker 已安装，跳过"
fi

# 2. 安装 Docker Compose（如果未安装）
if ! docker compose version &> /dev/null; then
    echo "[2/6] 安装 Docker Compose..."
    mkdir -p /usr/local/lib/docker/cli-plugins
    curl -SL "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64" \
        -o /usr/local/lib/docker/cli-plugins/docker-compose
    chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
else
    echo "[2/6] Docker Compose 已安装，跳过"
fi

# 3. 克隆/更新代码
if [ -d "$DEPLOY_DIR/.git" ]; then
    echo "[3/6] 更新代码..."
    cd "$DEPLOY_DIR"
    git fetch origin
    git reset --hard "origin/$BRANCH"
else
    echo "[3/6] 克隆代码..."
    rm -rf "$DEPLOY_DIR"
    git clone -b "$BRANCH" "$REPO_URL" "$DEPLOY_DIR"
    cd "$DEPLOY_DIR"
fi

echo "    当前版本: $(git log --oneline -1)"

# 4. 确认 .env.prod 存在
if [ ! -f backend/.env.prod ]; then
    echo "[4/6] ⚠️  backend/.env.prod 不存在！请先创建环境配置文件"
    exit 1
fi
echo "[4/6] 环境配置已就绪"

# 5. 配置 Docker 镜像加速（国内）
DOCKER_DAEMON_JSON="/etc/docker/daemon.json"
if [ ! -f "$DOCKER_DAEMON_JSON" ] || ! grep -q "registry-mirrors" "$DOCKER_DAEMON_JSON"; then
    echo "[5/6] 配置 Docker 镜像加速..."
    mkdir -p /etc/docker
    cat > "$DOCKER_DAEMON_JSON" <<'EOF'
{
    "registry-mirrors": [
        "https://docker.1ms.run",
        "https://docker.xuanyuan.me"
    ]
}
EOF
    systemctl daemon-reload
    systemctl restart docker
    echo "    镜像加速已配置，Docker 已重启"
else
    echo "[5/6] Docker 镜像加速已配置，跳过"
fi

# 6. 构建并启动服务
echo "[6/6] 构建并启动服务..."
cd "$DEPLOY_DIR"
docker compose -f docker-compose.prod.yml down --remove-orphans 2>/dev/null || true
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d

# 等待服务启动
echo ""
echo "等待服务启动..."
sleep 10

# 显示状态
echo ""
echo "========================================="
echo " 部署完成！"
echo "========================================="
echo ""
docker compose -f docker-compose.prod.yml ps
echo ""
echo "前端访问: http://$(hostname -I | awk '{print $1}')"
echo "后端 API: http://$(hostname -I | awk '{print $1}'):8000"
echo "API 文档: http://$(hostname -I | awk '{print $1}'):8000/docs"
echo ""
echo "查看日志: cd $DEPLOY_DIR && docker compose -f docker-compose.prod.yml logs -f"
