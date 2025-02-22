# Velez

DevOps/CloudOps CLI framework for making work with Terragrunt and performing various cloud operations much easier.

<a href="https://gitmoji.dev">
  <img
    src="https://img.shields.io/badge/gitmoji-%20😜%20😍-FFDD67.svg?style=flat-square"
    alt="Gitmoji"
  />
</a>


![Velez](img/velez.jpg)


## Features

- Supporting following services/tools and operations on them:
    - Terragrunt:
        - Walk directory structure containing Terragrunt modules.
        - Run Plan on a selected module or a specific target.
        - Run Apply on a selected module or a specific target.
        - Import a resource to the state.
        - Run Destroy on a selected module or a specific target.
        - Run Output on a selected module or a specific target.
        - Run Validate on a selected module.
        - Run Refresh on a selected module.
        - Run State operations like:
            - List resources.
            - Move a resource.
            - Remove a resource.
            - Show resource.
            - Pull and push state.
        - Run Module operations on source modules:
            - Move a module to a new directory, including moving remote state.
            - Destroy resources and backend of the module.
            - Destroy backend of the module.
        - Taint and Untaint a resource.
        - Unlock module and show lock information.
    - File operations:
        - Formatting all HCL files in the project.
        - Cleaning up temporary files in the project or a selected module.


## Installation

Framework is written in Python and can be installed as a package.

1. Clone the repository:
    ```sh
    git clone https://github.com/devops-infra/velez.git
    ```
2. Navigate to the project directory:
    ```sh
    cd velez
    ```
3. Install other dependencies:
    * Install Python if not installed yet - required.
    * Install `hcledit` - required for updating `.hcl` files.
    * Install `direnv` if not installed yet - highly suggested for managing environments. 

    It can be installed, e.g. by running:
    ```sh
    brew install python
    brew install direnv
    brew install minamijoyo/hcledit/hcledit
    ```
4. Install the package:
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
* `<other-arguments>` are additional arguments for the Terraform and Terragrunt operations, e.g.
  `--target=module.resource`.

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
velez -tg plan aws/dev-account
``` 


## Configuration

Velez expects following environment variables to be set if corresponding values are not hardcoded in the root Terragrunt
configuration file:

* `VELEZ_ROOT_HCL` - relative path to the Terragrunt configuration file, e.g. `root.hcl`.
* `VELEZ_TEMP_CONFIG` - absolute path to a temporary file created to render Terragrunt configuration, e.g.
  `/tmp/terragrunt.hcl`.

For the convenience, these variables can be set in a `.env` file in the project directory and use the `direnv` (mentioned above) to load
them automatically for every project separately.

Veles will read Terragrunt configuration and expand any dynamic config available statically. 
For example for each selected Terragrunt module backed configuration will be read to determine exact values of the S3 bucket and DynamoDB table and key used for locking the state.



## License

This project is licensed under the MIT License.

## Velez

Name of the project is a misspelled name of the slavic god of the
underworld - [Veles](https://en.wikipedia.org/wiki/Veles_(god)).
