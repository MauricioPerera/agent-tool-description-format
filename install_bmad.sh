#!/bin/bash

# BMAD-METHOD Installation Script for Linux/macOS
# ATDF Project Integration Setup
# Version: 1.0.0

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "\n${BLUE}[STEP $1]${NC} $2"
}

# Header
echo
echo "========================================"
echo "  BMAD-METHOD Installation for ATDF"
echo "========================================"
echo

log_info "Starting BMAD-METHOD installation..."
echo

# Check if running with sudo (not recommended for npm)
if [[ $EUID -eq 0 ]]; then
    log_warning "Running as root is not recommended for npm operations"
    log_warning "Consider running without sudo for better security"
    echo
fi

# Step 1: Check Node.js installation
log_step "1/7" "Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    log_error "Node.js is not installed or not in PATH"
    echo "Please install Node.js from https://nodejs.org/"
    echo "Minimum required version: 20.0.0"
    echo
    echo "Installation options:"
    echo "  Ubuntu/Debian: curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt-get install -y nodejs"
    echo "  CentOS/RHEL:   curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash - && sudo yum install -y nodejs"
    echo "  macOS:         brew install node"
    exit 1
else
    log_success "Node.js is installed"
    node --version
fi
echo

# Step 2: Check Python installation
log_step "2/7" "Checking Python installation..."
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    log_error "Python is not installed or not in PATH"
    echo "Please install Python from https://python.org/"
    echo "Minimum required version: 3.8.0"
    echo
    echo "Installation options:"
    echo "  Ubuntu/Debian: sudo apt-get update && sudo apt-get install -y python3 python3-pip"
    echo "  CentOS/RHEL:   sudo yum install -y python3 python3-pip"
    echo "  macOS:         brew install python"
    exit 1
else
    log_success "Python is installed"
    if command -v python3 &> /dev/null; then
        python3 --version
        PYTHON_CMD="python3"
        PIP_CMD="pip3"
    else
        python --version
        PYTHON_CMD="python"
        PIP_CMD="pip"
    fi
fi
echo

# Step 3: Check project configuration
log_step "3/7" "Checking project configuration..."
if [[ ! -f "package.json" ]]; then
    log_error "package.json not found in current directory"
    echo "Please run this script from the ATDF project root directory"
    exit 1
else
    log_success "package.json found"
fi

if [[ ! -f "bmad.config.yml" ]]; then
    log_error "bmad.config.yml not found"
    echo "Please ensure BMAD configuration is present"
    exit 1
else
    log_success "bmad.config.yml found"
fi
echo

# Step 4: Install Node.js dependencies
log_step "4/7" "Installing Node.js dependencies..."
log_info "Running npm install..."
if npm install; then
    log_success "Node.js dependencies installed successfully"
else
    log_error "Failed to install Node.js dependencies"
    exit 1
fi
echo

# Step 5: Install Python dependencies
log_step "5/7" "Installing Python dependencies..."
log_info "Upgrading pip..."
$PYTHON_CMD -m pip install --upgrade pip --user

log_info "Installing Python requirements..."
if [[ -f "requirements.txt" ]]; then
    if $PYTHON_CMD -m pip install -r requirements.txt --user; then
        log_success "Python dependencies installed successfully"
    else
        log_error "Failed to install Python dependencies"
        exit 1
    fi
else
    log_warning "requirements.txt not found, skipping Python dependencies"
fi
echo

# Step 6: Install BMAD-METHOD
log_step "6/7" "Installing BMAD-METHOD..."
log_info "Installing BMAD-METHOD via npm..."

# Try global installation first, then local if it fails
if npm install -g bmad-method 2>/dev/null; then
    log_success "BMAD-METHOD installed globally"
elif npm install bmad-method; then
    log_success "BMAD-METHOD installed locally"
    log_warning "Global installation failed, using local installation"
else
    log_error "Failed to install BMAD-METHOD"
    echo "Please check your npm configuration and try again"
    exit 1
fi
echo

# Step 7: Setup BMAD-ATDF Integration
log_step "7/7" "Setting up BMAD-ATDF Integration..."
log_info "Running BMAD-ATDF integration setup..."

if [[ -f "tools/bmad_atdf_integration.py" ]]; then
    if $PYTHON_CMD tools/bmad_atdf_integration.py; then
        log_success "BMAD-ATDF integration setup completed"
    else
        log_warning "BMAD-ATDF integration setup encountered issues"
        echo "Please check the logs and run manually if needed"
    fi
else
    log_warning "BMAD-ATDF integration script not found"
    echo "Please ensure tools/bmad_atdf_integration.py exists"
fi
echo

# Create BMAD directories if they don't exist
log_info "Ensuring BMAD directory structure..."
mkdir -p bmad/{tools,agents,workflows}
log_success "BMAD directory structure verified"

echo
echo "========================================"
echo "  BMAD-METHOD Installation Complete!"
echo "========================================"
echo
log_success "BMAD-METHOD has been successfully installed and configured for ATDF"
echo

echo "Next Steps:"
echo "1. Visit https://gemini.google.com or https://chat.openai.com"
echo "2. Upload the bmad-orchestrator.md file from bmad/agents/"
echo "3. Start with: *help or *status"
echo

echo "Available Commands:"
echo "  npm run bmad:update    - Update BMAD-METHOD"
echo "  npm run bmad:status    - Check BMAD status"
echo "  npm run bmad:tools     - List available tools"
echo "  npm run bmad:agents    - List configured agents"
echo

echo "Documentation:"
echo "  - BMAD Configuration: bmad.config.yml"
echo "  - Agent Definitions: bmad/agents/"
echo "  - Workflow Definitions: bmad/workflows/"
echo "  - Tool Definitions: bmad/tools/"
echo "  - Project Brief: bmad/project_brief.md"
echo

echo "For support and documentation:"
echo "  - ATDF Docs: docs/ATDF_SPECIFICATION.md"
echo "  - BMAD-METHOD: https://github.com/bmad-code-org/BMAD-METHOD"
echo "  - Issues: https://github.com/your-repo/agent-tool-description-format/issues"
echo

# Check if installation was successful
if [[ -f "bmad/bmad_status.json" ]]; then
    log_info "BMAD integration status file found"
    log_success "Installation verification successful"
else
    log_warning "BMAD status file not found"
    echo "Installation may be incomplete"
fi

echo
log_success "Installation script completed successfully!"

exit 0