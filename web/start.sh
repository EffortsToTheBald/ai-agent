#!/bin/bash
# 启动脚本：同时启动 FastAPI 后端和 React 前端

cd "$(dirname "$0")"

echo "=== 启动 FastAPI 后端 ==="
cd backend
source ../.venv/bin/activate 2>/dev/null || source ../../ai-agent-venv/bin/activate
pip install -r requirements.txt -q
cd ..

echo "=== 启动 React 前端 ==="
cd frontend
npm install
npm run dev &

echo "=== 启动 FastAPI 后端 ==="
cd ../backend
python main.py &

echo ""
echo "=========================================="
echo "  前端: http://localhost:3000"
echo "  后端: http://localhost:8000"
echo "  API 文档: http://localhost:8000/docs"
echo "=========================================="
echo ""
echo "按 Ctrl+C 停止所有服务"

wait
