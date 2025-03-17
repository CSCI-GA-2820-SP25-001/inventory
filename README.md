# eCommerce Inventory System


[![Build Status](https://github.com/nyu-devops/inventory/actions/workflows/ci.yml/badge.svg)](https://github.com/nyu-devops/inventory/actions)
[![codecov](https://codecov.io/gh/nyu-devops/inventory/branch/master/graph/badge.svg?token=y6OUlCB4bC)](https://codecov.io/gh/nyu-devops/inventory)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-red.svg)](https://www.python.org/)
[![Open in Remote - Containers](https://img.shields.io/static/v1?label=Remote%20-%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/nyu-devops/inventory)

## Introduction

<!-- Brief project introduction -->
Managing inventory effectively is critical for any eCommerce business. This project focuses on building a scalable inventory management system that enables retailers to efficiently track stock levels, manage suppliers, and handle product orders using a RESTful API.

<!-- Description of inventory resource functionality -->
The inventory resource keeps track of how many of each product we have in our warehouse. At a minimum, it should reference a product ID and the quantity on hand. Inventory should also track restock levels and the condition of the item (i.e., new, open box, used). Restock levels will help determine when to order more products. Being able to query products by their condition (e.g., new, used) could be very useful.

This project follows **Test-Driven Development (TDD)** principles, ensuring robust and reliable functionality. It uses `Flask` for API development and `SQLAlchemy` for database management.

## Prerequisites

<!-- List of required software for setup -->
This project uses **Docker** and **Visual Studio Code** with the Remote Containers extension for a consistent development environment.

You will need:

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Visual Studio Code](https://code.visualstudio.com)
- [Remote Containers Extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

Alternatively, you can use **Vagrant** and **VirtualBox** for setting up the environment.

## Bring up the development environment

To bring up the development environment you should clone this repo, change into the repo directory:

```bash
git clone https://github.com/nyu-devops/inventory.git
cd inventory
```

Depending on which development environment you created, pick from the following:

### Start developing with Visual Studio Code and Docker

Open Visual Studio Code using the `code .` command. VS Code will prompt you to reopen in a container and you should say **yes**. This will take a while as it builds the Docker image and creates a container from it to develop in.

```bash
code .
```

Note that there is a period `.` after the `code` command. This tells Visual Studio Code to open the editor and load the current folder of files.

Once the environment is loaded you should be placed at a `bash` prompt in the `/app` folder inside of the development container. This folder is mounted to the current working directory of your repository on your computer. This means that any file you edit while inside of the `/app` folder in the container is actually being edited on your computer. You can then commit your changes to `git` from either inside or outside of the container.

### Using Vagrant and VirtualBox

Bring up the virtual machine using Vagrant.

```shell
vagrant up
vagrant ssh
cd /vagrant
```

This will place you in the virtual machine in the `/vagrant` folder which has been shared with your computer so that your source files can be edited outside of the VM and run inside of the VM.

## Running the tests

As developers we always want to run the tests before we change any code. That way we know if we broke the code or if someone before us did. Always run the test cases first!

Run the unit tests using `pytest`

```shell
make test
```

PyTest is configured via the included `setup.cfg` file to automatically include the `--pspec` flag so that red-green-refactor is meaningful. If you are in a command shell that supports colors, passing tests will be green while failing tests will be red.

PyTest is also configured to automatically run the `coverage` tool and you should see a percentage-of-coverage report at the end of your tests. If you want to see what lines of code were not tested use:

```shell
coverage report -m
```

This is particularly useful because it reports the line numbers for the code that have not been covered so you know which lines you want to target with new test cases to get higher code coverage.

You can also manually run `pytest` with `coverage` (but settings in `pyporojrct.toml` do this already)

```shell
$ pytest --pspec --cov=service --cov-fail-under=95
```

Try and get as close to 100% coverage as you can.

It's also a good idea to make sure that your Python code follows the PEP8 standard. Both `flake8` and `pylint` have been included in the `pyproject.toml` file so that you can check if your code is compliant like this:

```shell
make lint
```

Which does the equivalent of these commands:

```shell
flake8 service tests --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 service tests --count --max-complexity=10 --max-line-length=127 --statistics
pylint service tests --max-line-length=127
```

Visual Studio Code is configured to use `pylint` while you are editing. This catches a lot of errors while you code that would normally be caught at runtime. It's a good idea to always code with pylint active.

## Running the service

The project uses `honcho` which gets it's commands from the `Procfile`. To start the service simply use:

```shell
honcho start
```

As a convenience you can aso use:

```shell
make run
```

You should be able to reach the service at: http://localhost:8000. The port that is used is controlled by an environment variable defined in the `.flaskenv` file which Flask uses to load it's configuration from the environment by default.

## Shutdown development environment

If you are using Visual Studio Code with Docker, simply existing Visual Studio Code will stop the docker containers. They will start up again the next time you need to develop as long as you don't manually delete them.

If you are using Vagrant and VirtualBox, when you are done, you can exit and shut down the vm with:

```shell
exit
vagrant halt
```

If the VM is no longer needed you can remove it with:

```shell
vagrant destroy
```

## What's featured in the project?

- `service/__init__.py` -- establishes the Flask app factory
- `service/routes.py` -- the main Service routes using Python Flask
- `service/models.py` -- the data model using SQLAlchemy
- `tests/test_routes.py` -- test cases against the Pet service
- `tests/test_models.py` -- test cases against the Pet model

## API Overview

<!-- Overview of API endpoints -->
This system provides RESTful API endpoints to:

Create new inventory items
Retrieve inventory details
Update stock levels
Delete products from inventory
Manage suppliers and categories
Development Workflow

<!-- Development best practices -->
Clone the repo and set up the environment.
Implement new features using TDD.
Run tests before committing.
Open a pull request for code review.
Merge changes after approval.


## License

Copyright (c) 2016, 2024 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
