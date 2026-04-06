#!/bin/bash
set -e

echo "========================================="
echo "  NeuraProp AI — Development Setup"
echo "========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check prerequisites
echo -e "\n${YELLOW}Checking prerequisites...${NC}"

command -v node >/dev/null 2>&1 || { echo "Node.js is required. Install from https://nodejs.org"; exit 1; }
command -v pnpm >/dev/null 2>&1 || { echo "pnpm is required. Run: npm install -g pnpm"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "Docker is required. Install Docker Desktop."; exit 1; }

# Check for uv
if ! command -v uv >/dev/null 2>&1; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

echo -e "${GREEN}All prerequisites found!${NC}"

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo -e "\n${YELLOW}Creating .env from .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}.env created. Update it with your API keys.${NC}"
fi

# Install TypeScript dependencies
echo -e "\n${YELLOW}Installing TypeScript dependencies...${NC}"
pnpm install

# Install Python dependencies
echo -e "\n${YELLOW}Installing Python dependencies...${NC}"
uv sync

# Start infrastructure
echo -e "\n${YELLOW}Starting Docker services (PostgreSQL, Redis, LocalStack)...${NC}"
docker compose -f infra/docker/docker-compose.yml up -d

# Wait for PostgreSQL to be ready
echo -e "\n${YELLOW}Waiting for PostgreSQL...${NC}"
for i in {1..30}; do
    if docker exec neuraprop-postgres pg_isready -U neuraprop >/dev/null 2>&1; then
        echo -e "${GREEN}PostgreSQL is ready!${NC}"
        break
    fi
    sleep 1
done

# Run database migrations
echo -e "\n${YELLOW}Running database migrations...${NC}"
cd migrations && uv run alembic upgrade head && cd ..

echo -e "\n${GREEN}========================================="
echo "  Setup complete!"
echo ""
echo "  Start the gateway:  cd services/gateway && uv run uvicorn gateway.main:app --reload"
echo "  Start the consumer: cd services/agents && uv run python -m agents.consumer"
echo "  Start the dashboard: cd apps/dashboard && pnpm dev"
echo ""
echo "  API docs: http://localhost:8000/docs"
echo "  Dashboard: http://localhost:3000"
echo "=========================================${NC}"
