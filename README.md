# Velez

Python framework for interacting with a Terragrunt configurations and performing various cloud operations.

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

To use the Velez CLI, you have two options:

### Interactive Menu

Run the CLI without additional arguments to use the interactive menu:

```sh
velez
```

### Automation

Run the CLI with additional arguments for automation:

```sh
velez --terragrunt <operation> <module>
```

Replace `<operation>` with `plan`, `apply`, or `destroy`, `<module>` with the path to the specific module directory.


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
