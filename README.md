# Velez

Python framework for interacting with Terragrunt configurations and performing various cloud operations.

![Velez](velez.jpg)

<a href="https://gitmoji.dev">
  <img
    src="https://img.shields.io/badge/gitmoji-%20😜%20😍-FFDD67.svg?style=flat-square"
    alt="Gitmoji"
  />
</a>

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/devops-infra/velez.git
    ```
2. Navigate to the project directory:
    ```sh
    cd velez
    ```
3. Install the package:
    ```sh
    pip install .
    ```


## Usage

### Help

Run the CLI with the `--help` argument to see the available commands:

```sh
velez --help
```

To use the Velez CLI, you have two options:


### Interactive Menu

Run the CLI without additional arguments to use the interactive menu:

```sh
velez
```


### Automation

Run the CLI with additional arguments for automation/scripting:

```sh
velez --terragrunt <operation> <module> <other-arguments>
```

Where:
* `<operation>` is a Terraform/Terragrunt operation to perform, e.g. `plan`. 
* `<module>` is a relative path to a Terragrunt module to operate on, e.g. `aws/dev-account`. 
* `<other-arguments>` are additional arguments for the operation, e.g. `--target=module.resource`.

For example for the following directory structure:

```plaintext
. 
├── aws
│   ├── dev-account
│   │   └── terragrunt.hcl
│   ├── prod-account
│   │   └── terragrunt.hcl
│   └── aws.hcl
├── .env
└── root.hcl
```

Run the following command to plan the `aws/dev-account` module:

```sh
velez --terragrunt plan aws/dev-account
``` 


## Configuration

Velez expects following environment variables to be set:
* `VELEZ_USE_S3_BACKEND` - set to `true` if you use AWS S3 backend for storing Terraform state. Acts as set to `true` by default.
* `VELEZ_USE_DYNAMODB_LOCKS` - set to `true` if you use AWS DynamoDB for locking Terraform state. Acts as set to `true` by default.

For your convenience, you can set these variables in a `.env` file in the project directory and use the `dotenv` to load them.


## Features

- Supporting following services/tools and operations on them:
  - Terragrunt: 
    - Walk directory structure containing Terragrunt modules.
    - Run Plan on a selected module or a specific target.
    - Run Apply on a selected module or a specific target.
    - Import a resource to the state.
    - Run Destroy on a selected module or a specific target.
    - Run State operations like:
      - List resources.
      - Move a resource.
      - Remove a resource.
      - Show resource.
      - Pull and push state.
    - Run Module operations on source modules:
      - Move a module to a new directory, including backend references.
      - Destroy resources and backend of the module.
      - Destroy backend of the module.
    - Taint and Untaint a resource.
    - Unlock module.
    - Run Output on a selected module or a specific target.
    - Run Validate on a selected module.
    - Run Refresh on a selected module.


## License

This project is licensed under the MIT License.


## Velez

Name of the project is a misspelled name of the slavic god of the underworld - [Veles](https://en.wikipedia.org/wiki/Veles_(god)).
