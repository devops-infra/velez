# CloudOpser

Python framework for interacting with a Terragrunt configurations and performing various cloud operations.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/cloudopser.git
    ```
2. Navigate to the project directory:
    ```sh
    cd cloudopser
    ```
3. Install the package:
    ```sh
    pip install .
    ```

## Usage

To use the CloudOpser CLI, you have two options:

### Interactive Menu

Run the CLI without additional arguments to use the interactive menu:

```sh
cloudopser
```

### Automation

Run the CLI with additional arguments for automation:

```sh
cloudopser --operation <operation> --module <module> --base_dir <base_dir>
```

Replace `<operation>` with `plan`, `apply`, or `destroy`, `<module>` with the path to the specific module directory, and `<base_dir>` with the path to the base directory.

## Features

- Main menu to choose services (currently only `Terragrunt`)
- Explore folders containing Terragrunt modules recursively
- List all modules with `terragrunt.hcl` files
- Run `terragrunt plan` on a selected module
- Run `terragrunt apply` on a selected module
- Run `terragrunt destroy` on a selected module
- All menus include `Back` and `Exit` options

## License

This project is licensed under the MIT License.
