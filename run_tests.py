#!/usr/bin/env python
"""Test runner script for the VIN Decoder Bot."""

import sys
import os
import subprocess
import argparse
from pathlib import Path


def run_command(cmd: list, cwd: str = None) -> int:
    """Run a command and return the exit code."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd)
    return result.returncode


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description="Run tests for VIN Decoder Bot")
    parser.add_argument(
        "--type",
        choices=["unit", "integration", "e2e", "all"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run with coverage report"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--failfast",
        "-x",
        action="store_true",
        help="Stop on first failure"
    )
    parser.add_argument(
        "--markers",
        "-m",
        help="Run tests matching given mark expression"
    )
    parser.add_argument(
        "--keyword",
        "-k",
        help="Run tests matching given keyword expression"
    )
    parser.add_argument(
        "--parallel",
        "-n",
        type=int,
        help="Number of parallel workers"
    )
    
    args = parser.parse_args()
    
    # Build pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add test directory based on type
    if args.type == "unit":
        cmd.append("src/tests/unit")
        if not args.markers:
            cmd.extend(["-m", "unit"])
    elif args.type == "integration":
        cmd.append("src/tests/integration")
        if not args.markers:
            cmd.extend(["-m", "integration"])
    elif args.type == "e2e":
        cmd.append("src/tests/e2e")
        if not args.markers:
            cmd.extend(["-m", "e2e"])
    else:
        cmd.append("src/tests")
    
    # Add coverage if requested
    if args.coverage:
        cmd.extend([
            "--cov=src",
            "--cov-report=term-missing:skip-covered",
            "--cov-report=html:htmlcov",
            "--cov-report=xml",
            "--cov-fail-under=80"
        ])
    
    # Add other options
    if args.verbose:
        cmd.append("-vv")
    else:
        cmd.append("-v")
    
    if args.failfast:
        cmd.append("-x")
    
    if args.markers:
        cmd.extend(["-m", args.markers])
    
    if args.keyword:
        cmd.extend(["-k", args.keyword])
    
    if args.parallel:
        cmd.extend(["-n", str(args.parallel)])
    
    # Add color output
    cmd.append("--color=yes")
    
    # Run tests
    print("=" * 60)
    print("VIN Decoder Bot Test Suite")
    print("=" * 60)
    
    exit_code = run_command(cmd)
    
    if exit_code == 0:
        print("\n✅ All tests passed!")
        
        # Run additional checks if all tests pass
        if args.type in ["all", "unit"]:
            print("\n" + "=" * 60)
            print("Running Code Quality Checks")
            print("=" * 60)
            
            # Run type checking
            print("\n📝 Type checking with mypy...")
            mypy_code = run_command(["python", "-m", "mypy", "src", "--ignore-missing-imports"])
            
            # Run linting
            print("\n🔍 Linting with flake8...")
            flake8_code = run_command([
                "python", "-m", "flake8", "src",
                "--max-line-length=120",
                "--exclude=src/tests"
            ])
            
            # Run formatting check
            print("\n🎨 Checking formatting with black...")
            black_code = run_command([
                "python", "-m", "black", "--check", "src"
            ])
            
            # Run import sorting check
            print("\n📦 Checking import sorting with isort...")
            isort_code = run_command([
                "python", "-m", "isort", "--check-only", "src"
            ])
            
            if all(code == 0 for code in [mypy_code, flake8_code, black_code, isort_code]):
                print("\n✅ All code quality checks passed!")
            else:
                print("\n⚠️ Some code quality checks failed")
                exit_code = 1
    else:
        print("\n❌ Tests failed!")
    
    # Generate coverage report message
    if args.coverage and exit_code == 0:
        print("\n📊 Coverage report generated:")
        print("   - Terminal: See above")
        print("   - HTML: Open htmlcov/index.html")
        print("   - XML: coverage.xml")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())