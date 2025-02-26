import argparse
import os
import sys

from pick import pick
from velez.file_ops import FileOperations
from velez.terragrunt_ops import TerragruntOperations
from velez.utils import str_terragrunt_menu, str_file_menu, str_exit, get_terragrunt_version, get_terraform_version, \
    get_opentofu_version


class Velez:
    """
    Main class for Velez.
    """
    def __init__(self, base_dir=None):
        self.base_dir = base_dir if base_dir else os.getcwd()
        self.root_hcl = os.getenv('VELEZ_ROOT_HCL', 'root.hcl')  # Root Terragrunt config file
        self.temp_config = os.getenv('VELEZ_TEMP_CONFIG',
                                     '/tmp/terragrunt_rendered.json')  # Temporary file to store rendered config
        self.use_s3_backend = False  # If S3 backend is used, will be updated for each module separately
        self.use_dynamodb_locks = False  # If DynamoDB locks are used, will be updated for each module separately
        self.dynamodb_table = ''  # DynamoDB table name, will be updated for each module separately
        self.dynamodb_lockid = ''  # DynamoDB lock ID, will be updated for each module separately
        self.s3_bucket_name = ''  # S3 backend bucket name, will be updated for each module separately
        self.s3_state_key = ''  # S3 tfstate key, will be updated for each module separately
        self.s3_state_path = ''  # Full S3 tfstate path, will be updated for each module separately
        self.terragrunt_version = '' # Terragrunt version
        self.terraform_version = '' # Terraform version
        self.opentofu_version = '' # OpenTofu version
        self.terragrunt_ops = TerragruntOperations(self)
        self.file_ops = FileOperations(self)

    def main_menu(self) -> None:
        """
        Display main menu.
        :return: None
        """
        title = "Choose a service:"
        options = [
            str_terragrunt_menu,
            str_file_menu,
            str_exit
        ]
        option, index = pick(options, title)

        if option == str_terragrunt_menu:
            self.terragrunt_ops.folder_menu()
        elif option == str_file_menu:
            self.file_ops.file_menu()
        elif option == str_exit:
            sys.exit()

        self.main_menu()

    def run(self, terragrunt: bool=False, file: bool=False, **kwargs: dict) -> None:
        """
        Run the framework passing the arguments.
        :param terragrunt: run Terragrunt operations
        :param file: run file operations
        :param kwargs: additional arguments
        :return: None
        """
        self.terragrunt_version = get_terragrunt_version(quiet=True)
        self.terraform_version = get_terraform_version(quiet=True)
        self.opentofu_version = get_opentofu_version(quiet=True)
        if not self.terraform_version and not self.opentofu_version:
            print("Please install Terraform or OpenTofu to continue properly.")
        if not self.terragrunt_version:
            print("Please install Terragrunt to continue properly.")

        if terragrunt and kwargs.get('pos_args'):
            pos_args = kwargs.get('pos_args')
            option = pos_args[0]
            module = pos_args[1]
            additional_args = pos_args[2:]
            self.terragrunt_ops.run_terragrunt(arguments=[option] + additional_args)
        elif terragrunt:
            self.terragrunt_ops.folder_menu()
        elif file:
            self.file_ops.file_menu()
        else:
            self.main_menu()


def main() -> None:
    """
    Main function.
    :return: None
    """
    parser = argparse.ArgumentParser(description='Velez ∀')
    parser.add_argument('-tg', '--terragrunt', action='store_true', help='Run Terragrunt operations')
    parser.add_argument('-f', '--file', action='store_true', help='Run file operations')
    parser.add_argument('pos_args', nargs=argparse.REMAINDER, help='Arguments to pass further')
    args = parser.parse_args()

    framework = Velez()
    framework.run(terragrunt=args.terragrunt, file=args.file, pos_args=args.pos_args)


if __name__ == "__main__":
    main()
