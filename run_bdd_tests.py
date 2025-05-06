#!/usr/bin/env python3
"""
BDD Test Runner Script

This script provides a convenient way to run the BDD tests with different configurations.
"""

import os
import sys
import argparse
import subprocess


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Run BDD tests with behave and Selenium"
    )

    parser.add_argument(
        "--browser",
        choices=["chrome", "firefox"],
        default="chrome",
        help="Browser to use for testing (default: chrome)",
    )

    parser.add_argument(
        "--headless",
        action="store_true",
        default=True,
        help="Run browser in headless mode (default: True)",
    )

    parser.add_argument(
        "--no-headless",
        action="store_false",
        dest="headless",
        help="Run browser in visible mode",
    )

    parser.add_argument(
        "--feature",
        default=None,
        help="Specific feature file to run (default: all features)",
    )

    parser.add_argument(
        "--tags",
        default=None,
        help="Run scenarios with specific tags (e.g., @smoke, @regression)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Run with verbose output",
    )

    parser.add_argument(
        "--db-uri",
        default="sqlite:///test_admin.db",
        help="Database URI for testing",
    )

    return parser.parse_args()


def run_tests(args):
    """Run the BDD tests with the specified configuration"""
    # Set environment variables
    env = os.environ.copy()
    env["BROWSER"] = args.browser
    env["HEADLESS"] = str(args.headless).lower()
    env["DATABASE_URI"] = args.db_uri

    # Build the behave command
    cmd = ["behave"]

    # Add verbose flag if specified
    if args.verbose:
        cmd.append("-v")

    # Add tags if specified
    if args.tags:
        cmd.extend(["--tags", args.tags])

    # Add specific feature file if specified
    if args.feature:
        cmd.append(args.feature)

    # Print the command being run
    print(f"Running: {' '.join(cmd)}")
    print(f"Browser: {args.browser} (Headless: {args.headless})")
    print(f"Database URI: {args.db_uri}")
    print("-" * 80)

    # Run the command
    try:
        process = subprocess.run(cmd, env=env, check=True)
        return process.returncode
    except subprocess.CalledProcessError as e:
        print(f"Error running tests: {e}")
        return e.returncode


if __name__ == "__main__":
    args = parse_args()
    sys.exit(run_tests(args))
