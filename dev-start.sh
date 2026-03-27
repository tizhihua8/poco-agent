#!/bin/bash
# Poco 本地开发启动脚本（EM 在 Docker 中运行）

set -e

echo "🚀 启动 Poco 本地开发环境..."

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查是否在项目根目录
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ 请在项目根目录运行此脚本"
    exit 1
fi

# 1. 构建本地镜像（首次或代码修改后）
echo -e "\n${BLUE}🔨 检查本地镜像...${NC}"

if ! docker images | grep -q "poco-executor-manager:local"; then
    echo -e "${YELLOW}⚠️  EM Manager 本地镜像不存在，开始构建...${NC}"
    docker build -t poco-executor-manager:local \
        -f docker/executor_manager/Dockerfile \
        .
    echo -e "${GREEN}✅ EM Manager 镜像构建完成${NC}"
else
    # 镜像已存在，询问是否需要重建
    echo -e "${GREEN}✅ EM Manager 本地镜像已存在${NC}"
    read -p "是否重新构建镜像？[y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker build -t poco-executor-manager:local \
            -f docker/executor_manager/Dockerfile \
            .
        echo -e "${GREEN}✅ EM Manager 镜像构建完成${NC}"
    fi
fi

# 2. 启动依赖服务（包括 EM Manager）
echo -e "\n${BLUE}📦 启动 Docker 服务 (postgres, rustfs)...${NC}"
docker-compose up -d postgres rustfs

echo -e "\n${BLUE}📦 启动 Executor Manager（不启动 backend 依赖）...${NC}"
docker-compose up -d --no-deps executor-manager

# 等待服务就绪
echo "⏳ 等待服务启动..."
sleep 5

# 3. 验证 EM Manager 容器是否使用本地镜像
EM_IMAGE=$(docker-compose images executor-manager | awk 'NR==2 {print $2":"$3}')
if [[ "$EM_IMAGE" == "poco-executor-manager:local" ]]; then
    echo -e "${GREEN}✅ EM Manager 使用本地镜像${NC}"
else
    echo -e "${RED}❌ EM Manager 未使用本地镜像 (当前: $EM_IMAGE)${NC}"
    echo -e "${YELLOW}检查 .env 中 EXECUTOR_MANAGER_IMAGE 配置${NC}"
fi

# 4. 检查端口占用
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo -e "${YELLOW}⚠️  端口 $1 已被占用${NC}"
        return 1
    fi
    return 0
}

check_port 8000 || echo "Backend 可能已在运行"
check_port 3000 || echo "Frontend 可能已在运行"

# 5. 提示启动命令
echo -e "\n${GREEN}✅ Docker 服务已启动${NC}"
echo -e "\n请在不同终端中运行以下命令："
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}1. Backend:${NC}"
echo -e "   ${GREEN}cd backend && uv sync && uv run python -m app.main${NC}"
echo -e "\n${BLUE}2. Frontend:${NC}"
echo -e "   ${GREEN}cd frontend && pnpm dev${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "\n${YELLOW}Docker 服务:${NC}"
echo "  - EM Manager:   http://localhost:8001 (poco-executor-manager:local)"
echo "  - PostgreSQL:   localhost:5432"
echo "  - RustFS:       localhost:9000"
echo -e "\n${YELLOW}本地服务:${NC}"
echo "  - Backend:      http://localhost:8000"
echo "  - Frontend:     http://localhost:3000"
echo -e "\n${YELLOW}查看 EM 日志:${NC}"
echo "  docker-compose logs -f executor-manager"
echo -e "\n${YELLOW}重建 EM 镜像:${NC}"
echo "  docker build -t poco-executor-manager:local -f docker/executor_manager/Dockerfile ."
echo -e "\n${YELLOW}停止服务:${NC}"
echo "  ./dev-stop.sh"

# 6. 可选：使用 tmux 启动本地服务
if command -v tmux &> /dev/null && [ "$1" == "--tmux" ]; then
    echo -e "\n${BLUE}🚀 使用 tmux 启动本地服务...${NC}"

    tmux new-session -d -s poco "cd backend && uv sync && uv run python -m app.main"
    tmux rename-window -t poco:0 backend

    tmux new-window -t poco:1 -n frontend "cd frontend && pnpm dev"

    tmux attach-session -t poco
fi
