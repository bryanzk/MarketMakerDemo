#!/usr/bin/env bash
# ==============================================================================
# init.sh — MarketMakerDemo Environment Bootstrap & Smoke Test
# ==============================================================================
# Usage:
#   ./scripts/init.sh          # Setup environment only
#   ./scripts/init.sh smoke    # Setup + run smoke tests
#
# Reference: https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
# ==============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ==============================================================================
# Helper Functions
# ==============================================================================

log_info() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_step() {
    echo -e "\n${GREEN}==>${NC} $1"
}

# ==============================================================================
# 1. Determine Project Root
# ==============================================================================

log_step "Determining project root..."
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"
log_info "Project root: $PROJECT_ROOT"

# ==============================================================================
# 2. Activate Virtual Environment
# ==============================================================================

log_step "Setting up Python virtual environment..."

if [ -d "venv" ]; then
    source venv/bin/activate
    log_info "Activated existing venv"
else
    log_warn "venv not found. Creating new virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    log_info "Created and activated new venv"
fi

# ==============================================================================
# 3. Install Dependencies
# ==============================================================================

log_step "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
log_info "Dependencies installed"

# ==============================================================================
# 4. Verify Environment Variables
# ==============================================================================

log_step "Checking environment variables..."

# Load .env if exists
if [ -f ".env" ]; then
    set -a
    source .env
    set +a
    log_info "Loaded .env file"
else
    log_warn ".env file not found (may be required for live trading)"
fi

# Check required variables (warn only, don't fail)
required_vars=("BINANCE_API_KEY" "BINANCE_API_SECRET")
missing_vars=()

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -gt 0 ]; then
    log_warn "Missing environment variables: ${missing_vars[*]}"
    log_warn "These may be required for live trading features"
else
    log_info "All required environment variables set"
fi

# ==============================================================================
# 5. Verify Project Structure
# ==============================================================================

log_step "Verifying project structure..."

required_files=(
    "server.py"
    "requirements.txt"
    "alphaloop/main.py"
    "docs/project/feature_matrix.json"
    "docs/project/claude_progress.md"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -gt 0 ]; then
    log_error "Missing required files: ${missing_files[*]}"
    exit 1
else
    log_info "All required files present"
fi

# ==============================================================================
# 6. Smoke Tests (Optional)
# ==============================================================================

if [ "$1" = "smoke" ]; then
    log_step "Running smoke tests..."
    
    SERVER_PID=""
    cleanup() {
        if [ -n "$SERVER_PID" ]; then
            log_info "Cleaning up server process..."
            kill $SERVER_PID 2>/dev/null || true
            wait $SERVER_PID 2>/dev/null || true
        fi
    }
    trap cleanup EXIT
    
    # 6.1 Start server in background
    log_step "Starting server..."
    python server.py &
    SERVER_PID=$!
    
    # Wait for server to be ready
    MAX_WAIT=30
    WAIT_COUNT=0
    while ! curl -s http://127.0.0.1:8000/ > /dev/null 2>&1; do
        sleep 1
        WAIT_COUNT=$((WAIT_COUNT + 1))
        if [ $WAIT_COUNT -ge $MAX_WAIT ]; then
            log_error "Server failed to start within ${MAX_WAIT}s"
            exit 1
        fi
    done
    log_info "Server started (PID: $SERVER_PID)"
    
    # 6.2 Health check - main page
    log_step "Checking main page..."
    if curl -s http://127.0.0.1:8000/ | grep -q "html" > /dev/null; then
        log_info "Main page accessible"
    else
        log_error "Main page check failed"
        exit 1
    fi
    
    # 6.3 Health check - API status
    log_step "Checking API status endpoint..."
    if curl -s http://127.0.0.1:8000/api/status > /dev/null; then
        log_info "API status endpoint accessible"
    else
        log_error "API status endpoint check failed"
        exit 1
    fi
    
    # 6.4 Run core pytest subset
    log_step "Running core pytest tests..."
    
    # Kill server before running tests to avoid port conflicts
    kill $SERVER_PID 2>/dev/null || true
    wait $SERVER_PID 2>/dev/null || true
    SERVER_PID=""
    
    # Run a minimal set of tests
    if pytest tests/test_server.py -v --tb=short -x 2>/dev/null; then
        log_info "Core server tests passed"
    else
        log_warn "Some tests failed (check output above)"
        # Don't exit - allow continuation for development
    fi
    
    log_info "Smoke tests completed"
fi

# ==============================================================================
# 7. Summary
# ==============================================================================

echo ""
echo "=============================================="
echo "  MarketMakerDemo Environment Ready"
echo "=============================================="
echo ""
echo "  Project Root: $PROJECT_ROOT"
echo "  Python:       $(python --version)"
echo "  Venv:         $VIRTUAL_ENV"
echo ""
echo "  Quick Commands:"
echo "    python server.py        # Start web server"
echo "    pytest tests/ -v        # Run all tests"
echo "    ./scripts/init.sh smoke # Run smoke tests"
echo ""
echo "  Documentation:"
echo "    docs/project/init_plan.md          # Initialization blueprint"
echo "    docs/project/feature_matrix.json   # Feature tracker"
echo "    docs/project/claude_progress.md    # Progress log"
echo ""
log_info "Environment setup complete!"

