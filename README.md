# Velez

DevOps/CloudOps CLI framework for making work with Terragrunt and performing various cloud operations much easier.

Do you want to automate your daily tasks with Terragrunt, Terraform, GitHub, and other tools? Velez is here to help you!

Do you sometimes forget to add changed files before pushing to GitHub? Velez will do that for you and even format HCL
files before committing!

<a href="https://gitmoji.dev">
  <img
    src="https://img.shields.io/badge/gitmoji-%20😜%20😍-FFDD67.svg?style=flat-square"
    alt="Gitmoji"
  />
</a>


## Advantages

- Terragrunt **backend configuration** is read by invoking `terragrunt` command, so it is **always up to date** and resembles the 
  **real state of the infrastructure**, not just hardcoded values in the code.
- All operations are performed in the **context of the current directory**, so you don't have to worry about running
  commands in the wrong environment.


## Disclaimer

**This project is in the early development stage and is not ready for production use. It is a work in progress and may
contain bugs, incomplete features, incorrect documentation, backward incompatible changes or other issues.
Use it at your own risk before it reaches 1.x.x version. Read the documentation carefully and test it in a 
safe environment before using it.**

Since it operates on the infrastructure, user is responsible for the consequences of the actions taken by the tool and
should review the code before using it.

![Velez](img/velez.jpg)


## Features

Supporting following services/tools and operations on them:

- Terragrunt operations `-tg` or `--terragrunt`:
    - Walk directory structure containing Terragrunt modules.
    - Run Plan, Apply, Destroy and Output on a selected module or a specific target.
    - Taint and Untaint a resource.
    - Unlock module and show lock information.
    - Run Validate and Refresh on a selected module.
    - Import a resource to the state.
    - Run State operations, like list, move, remove, show, pull and push.
    - Run Module operations on source modules:
        - Move a module to a new directory, including moving remote state.
        - Destroy resources and backend of the module.
        - Destroy backend of the module.
- File operations `-f` or :
    - Formatting all HCL files in the project.
    - Cleaning up temporary files in the project or a selected module.
- GitHub operations `-gh` or `--github`:
    - Source operations, like commit, amend, push, pull or rebase.
    - Branch operations, like create, change local or remote, delete local or remote.
    - Manage pull requests, like create, list in the repository or the whole organization.
    - Manage issues, like create, list in the repository or the whole organization.
    - Easily remove stale branches.
- Docker operations `-d` or `--docker`:
    - List images in the registry or save them to a file for later use.
    - Manage organization members, like invites or removes.
    - Manage organization groups.

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
    * Install Terragrunt, and Terraform or OpenTofu - required for IaaC operations.
    * Install `hcledit` - required for updating `.hcl` files.
    * Install `direnv` or similar solution - highly suggested for managing environments.

   It can be installed, e.g. by running:
    ```sh
    brew install python
    brew install terraform
    brew install terragrunt
    brew install direnv
    brew install minamijoyo/hcledit/hcledit
    ```
4. Install the package:
    ```sh
    pip install .
    ```

## Usage

Tool is designed to speed up the work, so it expects some conditions:
* It should be run in the project directory.
* It should be run with the `direnv` or similar solution to load environment variables automatically.
* It expects the project directory to be a Git repository.
* It expects the project directory to be a Terragrunt project with a `root.hcl` (or other defined by `VELEZ_TG_ROOT_HCL`) file.
* It expects the project directory to be a Docker project, with a project directory to be repository name and parent directory to be
  organization name or personal account name (excluding `-` characters from the folder name).

### Help

Run the CLI with the `--help` argument to see the available commands:

```sh
velez --help
```

To use the Velez CLI, you have three options:

### Interactive Menu

Run the CLI without additional arguments to use the interactive menu:

```sh
velez
```

### Interactive Menu for specific operation

#### Terragrunt operations (`-tg` or `--terragrunt`)

```sh
velez --terragrunt
```

#### File operations (`-f` or `--file`)

Show menu for file operations:

```sh
velez --file
```

#### GitHub operations (`-gh` or `--github`)

Show menu for GitHub operations:

```sh
velez --github
```

### Automation / CLI

Run the CLI with additional arguments for automation/scripting:

#### Terragrunt operations (`-tg` or `--terragrunt`)

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

Velez expects following environment variables to be set:

| Variable                        | Description                                                                                                                           | Required for operations | Default               |
|---------------------------------|---------------------------------------------------------------------------------------------------------------------------------------|-------------------------|-----------------------|
| `VELEZ_TG_ROOT_HCL`             | Relative path to the Terragrunt configuration file.                                                                                   | Terragrunt              | `root.hcl`            |
| `VELEZ_TG_TEMP_CONFIG`          | Absolute path to a temporary file created to render Terragrunt configuration.                                                         | Terragrunt              | `/tmp/terragrunt.hcl` |
| `GITHUB_TOKEN`                  | GitHub token for accessing the GitHub API.                                                                                            | GitHub                  | `N/A`                 |
| `GITHUB_STALE_BRANCHES_DAYS`    | Number of days after which branches are considered stale.                                                                             | GitHub                  | `45`                  |
| `GITHUB_STALE_BRANCHES_COMMITS` | Number of commits after which branches are considered stale.                                                                          | GitHub                  | `30`                  |
| `DOCKER_USERNAME`               | Docker username for logging in to the Docker registry.                                                                                | Docker                  | `N/A`                 |
| `DOCKER_TOKEN`                  | Docker personal access token or organization access token for logging in to the Docker registry.                                      | Docker                  | `N/A`                 |
| `DOCKER_REPOSITORY`             | Default Docker repository for operations.                                                                                             | Docker                  | current directory     |
| `DOCKER_OWNER`                  | Default Docker owner of repositories.<br>Can be not set or set to Docker username for personal repositories, or to organization name. | Docker                  | parent directory      |
| `DOCKER_STALE_IMAGES_DAYS`      | Number of days after which images are considered stale.                                                                               | Docker                  | `30`                  |

For the convenience, these variables can be set in a `.envrc` or similar file in the project directory and use with the `direnv` (
mentioned above; or other similar software) to load them automatically for every project separately and use inheritance for the convenience.

Velez will read Terragrunt configuration to expand any dynamic load available config remotely.
For example for each selected Terragrunt module backed configuration will be read to determine exact values of the S3
bucket and DynamoDB table and key used for locking the state.

## License

This project is licensed under the MIT License.

## Velez

Name of the project is a misspelled name of the slavic god of the
underworld - [Veles](https://en.wikipedia.org/wiki/Veles_(god)).
