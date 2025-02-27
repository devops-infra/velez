import argparse
import os
import shutil
import sys

from pick import pick
from velez.file_ops import FileOperations
from velez.github_ops import GitHubOperations
from velez.terragrunt_ops import TerragruntOperations
from velez.utils import str_exit

str_terragrunt_menu = "⌘ Run Terragrunt"
str_file_menu = "⑇ File operations"
str_github_menu = "⇲ GitHub operations"


class Velez:
    """
    Main class for Velez.
    """

    def __init__(self, base_dir=None):
        self.base_dir = base_dir if base_dir else os.getcwd()
        self.terragrunt_ops = None
        self.file_ops = None
        self.github_ops = None

    def main_menu(self) -> None:
        """
        Display main menu.
        :return: None
        """
        title = "Choose a service:"
        options = [
            str_terragrunt_menu if self.check_terragrunt() else None,
            str_file_menu,
            str_github_menu if self.check_github() else None,
            str_exit
        ]
        options = [o for o in options if o]
        option, index = pick(options, title)

        if option == str_terragrunt_menu:
            if self.terragrunt_ops is None:
                self.terragrunt_ops = TerragruntOperations(self)
            self.terragrunt_ops.folder_menu()
        elif option == str_file_menu:
            if self.file_ops is None:
                self.file_ops = FileOperations(self)
            self.file_ops.file_menu()
        elif option == str_github_menu:
            if self.github_ops is None:
                self.github_ops = GitHubOperations(self)
            self.github_ops.github_menu()
        elif option == str_exit:
            sys.exit()

        self.main_menu()

    def run(self, terragrunt: bool = False, file: bool = False, github: bool = False, **kwargs: dict) -> None:
        """
        Run the framework passing the arguments.
        :param terragrunt: run Terragrunt operations
        :param file: run file operations
        :param github: run GitHub operations
        :param kwargs: additional arguments
        :return: None
        """
        if terragrunt and kwargs.get('pos_args'):
            pos_args = kwargs.get('pos_args')
            option = pos_args[0]
            # module = pos_args[1]
            additional_args = pos_args[2:]
            if self.terragrunt_ops is None:
                self.terragrunt_ops = TerragruntOperations(self)
            self.terragrunt_ops.run_terragrunt(arguments=[option] + additional_args)
        elif terragrunt:
            if self.terragrunt_ops is None:
                self.terragrunt_ops = TerragruntOperations(self)
            self.terragrunt_ops.folder_menu()
        elif file:
            if self.file_ops is None:
                self.file_ops = FileOperations(self)
            self.file_ops.file_menu()
        elif github:
            if self.github_ops is None:
                self.github_ops = GitHubOperations(self)
            self.github_ops.github_menu()
        else:
            self.main_menu()

    @staticmethod
    def check_github() -> bool:
        """
        Check if GitHub operations are possible.
        :return: True if possible, False otherwise
        """
        ok = True
        if not os.getenv('GITHUB_TOKEN'):
            ok = False
            print("Error: GITHUB_TOKEN environment variable not set.")
        if not shutil.which('git'):
            ok = False
            print("Error: git binary not found.")
        if not os.path.exists('.git'):
            ok = False
            print("Error: Not in a git repository.")
        if not ok:
            print("GitHub operations are not possible.")
        return ok

    @staticmethod
    def check_terragrunt() -> bool:
        ok = True
        if not shutil.which('terragrunt'):
            ok = False
            print("Error: Terragrunt binary not found.")
        if not shutil.which('terraform') and not shutil.which('tofu'):
            ok = False
            print("Error: Terraform or OpenTofu binaries not found.")
        if not ok:
            print("Terragrunt operations are not possible.")
        return ok


def main() -> None:
    """
    Main function.
    :return: None
    """
    parser = argparse.ArgumentParser(description='Velez ∀')
    parser.add_argument('-tg', '--terragrunt', action='store_true', help='Run Terragrunt operations')
    parser.add_argument('-f', '--file', action='store_true', help='Run file operations')
    parser.add_argument('-gh', '--github', action='store_true', help='Run GitHub operations')
    parser.add_argument('pos_args', nargs=argparse.REMAINDER, help='Arguments to pass further')
    args = parser.parse_args()

    framework = Velez()
    framework.run(terragrunt=args.terragrunt, file=args.file, github=args.github, pos_args=args.pos_args)


if __name__ == "__main__":
    main()
