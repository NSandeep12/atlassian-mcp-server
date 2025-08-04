#!/bin/bash

# =============================================================================
# Development Environment Setup Script for Atlassian MCP Server
# =============================================================================

set -e  # Exit on any error

echo "🚀 Setting up Atlassian MCP Server development environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3.11+ is installed
check_python() {
    print_status "Checking Python version..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
        
        if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 11 ]; then
            print_success "Python $PYTHON_VERSION found"
        else
            print_error "Python 3.11+ required, found $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 not found. Please install Python 3.11+"
        exit 1
    fi
}

# Check if Git is installed
check_git() {
    print_status "Checking Git installation..."
    if command -v git &> /dev/null; then
        GIT_VERSION=$(git --version | cut -d' ' -f3)
        print_success "Git $GIT_VERSION found"
    else
        print_error "Git not found. Please install Git"
        exit 1
    fi
}

# Create virtual environment
setup_venv() {
    print_status "Setting up Python virtual environment..."
    
    if [ -d "venv" ]; then
        print_warning "Virtual environment already exists. Removing..."
        rm -rf venv
    fi
    
    python3 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    print_success "Virtual environment created and activated"
}

# Install dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Dependencies installed"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
    
    # Install development dependencies
    print_status "Installing development dependencies..."
    pip install pytest pytest-cov black flake8 mypy pre-commit
    print_success "Development dependencies installed"
}

# Setup pre-commit hooks
setup_precommit() {
    print_status "Setting up pre-commit hooks..."
    
    if [ -f ".pre-commit-config.yaml" ]; then
        pre-commit install
        print_success "Pre-commit hooks installed"
    else
        print_warning "No .pre-commit-config.yaml found, skipping pre-commit setup"
    fi
}

# Setup environment file
setup_env() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        if [ -f "config/.env.example" ]; then
            cp config/.env.example .env
            print_success "Environment file created from example"
            print_warning "Please edit .env file with your actual credentials"
        else
            print_error "config/.env.example not found"
            exit 1
        fi
    else
        print_warning ".env file already exists, skipping"
    fi
}

# Create necessary directories
setup_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p logs data repos
    print_success "Directories created"
}

# Run tests to verify setup
run_tests() {
    print_status "Running tests to verify setup..."
    
    if [ -d "tests" ]; then
        python -m pytest tests/ -v
        print_success "Tests completed"
    else
        print_warning "No tests directory found, skipping tests"
    fi
}

# Main setup function
main() {
    echo "=============================================="
    echo "  Atlassian MCP Server Dev Setup"
    echo "=============================================="
    echo
    
    check_python
    check_git
    setup_venv
    install_dependencies
    setup_precommit
    setup_env
    setup_directories
    
    echo
    print_success "Development environment setup complete!"
    echo
    echo "Next steps:"
    echo "1. Edit .env file with your Jira and Bitbucket credentials"
    echo "2. Activate virtual environment: source venv/bin/activate"
    echo "3. Run the server: python src/main.py"
    echo "4. Run tests: python -m pytest tests/"
    echo
    echo "For more information, see README.md"
}

# Run main function
main "$@"
