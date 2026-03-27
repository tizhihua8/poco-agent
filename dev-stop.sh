#!/bin/bash
# Poco 本地开发停止脚本

echo "🛑 停止 Poco 本地开发环境..."

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. 停止 Docker 服务
echo -e "\n${BLUE}📦 停止 Docker 服务 (postgres, rustfs, executor-manager)...${NC}"
docker-compose down

# 2. 提示手动停止本地服务
echo -e "\n${GREEN}✅ Docker 服务已停止${NC}"
echo -e "\n请在各个终端按 ${BLUE}Ctrl+C${NC} 停止本地服务，或运行："
echo -e "  ${BLUE}pkill -f 'python -m app.main'${NC}  # 停止 Backend"
echo -e "  ${BLUE}pkill -f 'next dev'${NC}           # 停止 Frontend"

echo -e "\n${YELLOW}提示:${NC}"
echo "  - EM Manager 在 Docker 中运行，已被 docker-compose down 停止"
echo "  - EM 容器的挂载功能会在容器启动时通过 docker.sock 测试"
