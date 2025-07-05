#!/bin/bash

# Test runner script for TGIT

set -e

echo "🧪 Running TGIT Test Suite"
echo "=========================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
COVERAGE_THRESHOLD=80
VERBOSE=false
UNIT_ONLY=false
INTEGRATION_ONLY=false
WATCH=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -u|--unit)
            UNIT_ONLY=true
            shift
            ;;
        -i|--integration)
            INTEGRATION_ONLY=true
            shift
            ;;
        -w|--watch)
            WATCH=true
            shift
            ;;
        -c|--coverage)
            COVERAGE_THRESHOLD="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  -v, --verbose         Verbose output"
            echo "  -u, --unit           Run only unit tests"
            echo "  -i, --integration    Run only integration tests"
            echo "  -w, --watch          Watch mode (requires pytest-xdist)"
            echo "  -c, --coverage NUM   Coverage threshold (default: 80)"
            echo "  -h, --help           Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option $1"
            exit 1
            ;;
    esac
done

# Build pytest command
PYTEST_ARGS=()

# Add coverage options
PYTEST_ARGS+=("--cov=tgit" "--cov-report=term-missing" "--cov-report=html:htmlcov" "--cov-report=xml:coverage.xml")
PYTEST_ARGS+=("--cov-fail-under=$COVERAGE_THRESHOLD")

# Add verbosity
if [ "$VERBOSE" = true ]; then
    PYTEST_ARGS+=("-v")
fi

# Determine test path
if [ "$UNIT_ONLY" = true ]; then
    TEST_PATH="tests/unit"
    echo -e "${YELLOW}Running unit tests only${NC}"
elif [ "$INTEGRATION_ONLY" = true ]; then
    TEST_PATH="tests/integration"
    echo -e "${YELLOW}Running integration tests only${NC}"
else
    TEST_PATH="tests"
    echo -e "${YELLOW}Running all tests${NC}"
fi

# Watch mode
if [ "$WATCH" = true ]; then
    PYTEST_ARGS+=("-f")
    echo -e "${YELLOW}Watch mode enabled${NC}"
fi

# Run tests
echo -e "${YELLOW}Test command: pytest ${PYTEST_ARGS[*]} $TEST_PATH${NC}"
echo

if pytest "${PYTEST_ARGS[@]}" "$TEST_PATH"; then
    echo
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo -e "${GREEN}📊 Coverage report generated in htmlcov/index.html${NC}"
    
    # Open coverage report if on macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo -e "${YELLOW}Opening coverage report in browser...${NC}"
        open htmlcov/index.html
    fi
else
    echo
    echo -e "${RED}❌ Tests failed!${NC}"
    exit 1
fi