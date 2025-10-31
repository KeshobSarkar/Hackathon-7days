#!/bin/bash

# QIC LifePlus - Automated Setup Script for Linux
# This script automates the installation and initial setup process

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"

    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed"
        echo "Please install Node.js (v18+) from https://nodejs.org/"
        exit 1
    fi
    NODE_VERSION=$(node -v)
    print_success "Node.js found: $NODE_VERSION"

    # Check npm
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed"
        echo "npm should come with Node.js. Please reinstall Node.js"
        exit 1
    fi
    NPM_VERSION=$(npm -v)
    print_success "npm found: $NPM_VERSION"

    echo
}

# Install dependencies
install_dependencies() {
    print_header "Installing Dependencies"

    if [ -d "node_modules" ]; then
        print_info "node_modules already exists"
        read -p "Reinstall dependencies? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Skipping npm install"
            return
        fi
        rm -rf node_modules
    fi

    print_info "Running npm install... (this may take 2-5 minutes)"
    npm install

    if [ $? -eq 0 ]; then
        print_success "Dependencies installed successfully"
    else
        print_error "Failed to install dependencies"
        exit 1
    fi
    echo
}

# Build the project
build_project() {
    print_header "Building Project"

    print_info "Running npm run build..."
    npm run build

    if [ $? -eq 0 ]; then
        print_success "Production build successful"
        echo -e "${GREEN}Build output: dist/${NC}"
        du -sh dist/ 2>/dev/null || echo "  (Build folder size: check with 'du -sh dist/')"
    else
        print_error "Build failed"
        exit 1
    fi
    echo
}

# Display next steps
show_next_steps() {
    print_header "Setup Complete!"

    echo -e "${GREEN}QIC LifePlus is ready to run!${NC}\n"

    echo "Next steps:"
    echo
    echo -e "${BLUE}1. Start development server:${NC}"
    echo "   npm run dev"
    echo "   Then open: http://localhost:5173/"
    echo
    echo -e "${BLUE}2. Or run production build preview:${NC}"
    echo "   npx serve -s dist"
    echo "   Then open: http://localhost:3000/"
    echo
    echo -e "${BLUE}3. Explore the project:${NC}"
    echo "   - Edit src/pages/Dashboard.tsx to customize goals/tasks"
    echo "   - View YOUWARE.md for architecture details"
    echo "   - See INSTALL.md for full documentation"
    echo
    echo -e "${GREEN}Happy coding! 🚀${NC}"
    echo
}

# Main setup flow
main() {
    print_header "QIC LifePlus Setup Script"
    echo "This script will set up your development environment"
    echo

    # Check if we're in the right directory
    if [ ! -f "package.json" ]; then
        print_error "package.json not found"
        echo "Please run this script from the project root directory"
        exit 1
    fi

    check_prerequisites
    install_dependencies

    # Ask user if they want to build
    read -p "Build production version now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        build_project
    else
        print_info "Skipping build. Run 'npm run build' when ready"
        echo
    fi

    show_next_steps
}

# Run main function
main
