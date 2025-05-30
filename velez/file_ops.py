import json
import os
import shutil
import sys

import hcl2
from pick import pick
from velez.utils import STR_BACK, STR_EXIT, run_command

STR_FORMAT_FILES = "⎆ Format HCL files"
STR_CLEAN_FILES = "⌧ Clean temporary files"


class FileOperations:
    """
    Class for file operations.
    """

    def __init__(self, velez):
        self.velez = velez

    def file_menu(self) -> None:
        """
        File operations menu.
        :return: None
        """
        title = "Choose a file operation:"
        options = [
            STR_FORMAT_FILES,
            STR_CLEAN_FILES,
            STR_BACK,
            STR_EXIT
        ]
        option, index = pick(options, title)

        if option == STR_BACK:
            self.velez.main_menu()
        elif option == STR_EXIT:
            sys.exit()
        elif option == STR_FORMAT_FILES:
            self.format_hcl_files()
        elif option == STR_CLEAN_FILES:
            self.clean_files()

        self.file_menu()

    def format_hcl_files(self) -> None:
        """
        Format all HCL files.
        :return: None
        """
        print("Formatting HCL files...")
        if self.velez.check_terragrunt():
            run_command(['terragrunt', 'hclfmt'])
            if self.velez.get_tf_ot() == 'terraform':
                run_command(['terraform', 'fmt', '-recursive', '.'])
            elif self.velez.get_tf_ot() == 'tofu':
                run_command(['tofu', 'fmt', '-recursive', '.'])

    @staticmethod
    def clean_files(clean_path: str = '.') -> None:
        """
        Clean temporary files from Terraform and Terragrunt.
        :param clean_path: root path to start cleaning from
        :return: None
        """
        print(f"Cleaning temporary files in {clean_path}")
        for root, dirs, files in os.walk(clean_path):
            if ".terraform" in dirs:
                dir_to_remove = os.path.join(root, '.terraform')
                try:
                    shutil.rmtree(dir_to_remove)
                    print(f"Removed {dir_to_remove}")
                except Exception as e:
                    print(f"Error removing {dir_to_remove}: {e}")
            elif "registry.terraform.io" in dirs:
                dir_to_remove = os.path.join(root, 'registry.terraform.io')
                try:
                    shutil.rmtree(dir_to_remove)
                    print(f"Removed {dir_to_remove}")
                except Exception as e:
                    print(f"Error removing {dir_to_remove}: {e}")
            # ignore .terragrunt-cache folder in main terragrunt directory if it has .gitkeep file
            elif ".terragrunt-cache" in dirs:
                for file in files:
                    if file == '.gitkeep':
                        print(f"Skipping {os.path.join(root, '.terragrunt-cache')}")
                        break
                # remove the directory if it doesn't have .gitkeep file
                dir_to_remove = os.path.join(root, '.terragrunt-cache')
                try:
                    shutil.rmtree(dir_to_remove)
                    print(f"Removed {dir_to_remove}")
                except Exception as e:
                    print(f"Error removing {dir_to_remove}: {e}")
            for file in files:
                if file in ['.terraform.lock.hcl', 'terragrunt-debug.tfvars.json', 'tfplan']:
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                        print(f"Removed {file_path}")
                    except Exception as e:
                        print(f"Error removing {file_path}: {e}")
        input("Press Enter to return to the file menu...")

    @staticmethod
    def load_hcl_file(hcl_file: str) -> dict:
        """
        Load HCL file into a dictionary.
        :param hcl_file: HCL file to load
        :return: dictionary of HCL file
        """
        with open(hcl_file, 'r') as fr:
            return hcl2.load(fr)

    @staticmethod
    def load_json_file(json_file: str) -> dict:
        """
        Load JSON file into a dictionary.
        :param json_file: JSON file to load
        :return: dictionary of JSON file
        """
        with open(json_file, 'r') as fr:
            return json.load(fr)
