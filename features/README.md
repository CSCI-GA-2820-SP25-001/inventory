# BDD Testing Framework with Behave and Selenium

This directory contains a Behavior-Driven Development (BDD) testing framework using behave and Selenium for automated UI testing of the Admin UI.

## Overview

The framework uses:
- **behave**: For BDD-style testing with Gherkin syntax
- **Selenium**: For browser automation and UI interaction
- **WebDriver**: Chrome or Firefox driver for browser control

## Directory Structure

```
features/
├── admin_ui.feature       # Feature file with Gherkin scenarios
├── environment.py         # Setup and teardown hooks
├── steps/
│   └── admin_ui_steps.py  # Step definitions implementing the Gherkin steps
└── README.md              # This documentation file
```

## Feature File

The `admin_ui.feature` file contains Gherkin scenarios that describe the behavior of the Admin UI. Each scenario is written in a human-readable format that describes the expected behavior from a user's perspective.

## Environment Setup

The `environment.py` file handles:
- Setting up the Flask application for testing
- Configuring the Selenium WebDriver (Chrome or Firefox)
- Creating test data in the database
- Cleaning up after tests

## Step Definitions

The `steps/admin_ui_steps.py` file contains the Python code that implements each step in the Gherkin scenarios. These step definitions use Selenium to interact with the browser and verify the expected behavior.

## Running the Tests

To run the BDD tests:

```bash
# Run all tests
behave

# Run a specific feature file
behave features/admin_ui.feature

# Run a specific scenario (by line number)
behave features/admin_ui.feature:12

# Run with more verbose output
behave -v

# Run with specific browser (default is Chrome)
BROWSER=firefox behave

# Run in non-headless mode (to see the browser)
HEADLESS=false behave
```

## Configuration Options

The framework can be configured using environment variables:

- `BROWSER`: Set to `chrome` or `firefox` (default: `chrome`)
- `HEADLESS`: Set to `true` or `false` to control headless mode (default: `true`)
- `DATABASE_URI`: Database connection string (default: `sqlite:///test_admin.db`)

## Adding New Tests

To add new tests:

1. Add new scenarios to the feature file using Gherkin syntax
2. Implement any new steps in the step definitions file
3. Run the tests to verify the new scenarios

## Troubleshooting

Common issues:

- **WebDriver not found**: Make sure you have the appropriate browser installed
- **Connection refused**: Ensure the Flask app is running on port 5000
- **Element not found**: Check if the element selectors are correct or if you need to add wait conditions
