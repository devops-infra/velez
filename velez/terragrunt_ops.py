import os
import re
import sys

import boto3
from pick import pick
from velez.file_ops import FileOperations
from velez.utils import run_command, str_back, str_exit

str_plan = "▷ Plan"
str_apply = "▶︎ Apply"
str_import = "◁ Import"
str_destroy = "⌧ Destroy"
str_output = "✉︎ Output"
str_init = "✦ Initialize"
str_validate = "☑ Validate"
str_refresh = "♻ Refresh"
str_state_menu = "⌖ State operations"
str_state_list = "⌸ List"
str_state_move = "↔ Move"
str_state_rm = "⌧ Remove"
str_state_show = "⎚ Show"
str_state_pull = "↓ Pull"
str_state_push = "↑ Push"
str_module_menu = "⎄ Module operations"
str_module_move = "↔ Move module"
str_module_destroy = "⌧ Destroy module"
str_module_destroy_backend = "⌧ Destroy backend"
str_taint_menu = "☣︎ Taint operations"
str_taint = "☣ Taint"
str_untaint = "♺️ Untaint"
str_lock_menu = "⎉ Lock operations"
str_lock_info = "ℹ Lock info"
str_unlock = "⇭ Unlock"
str_clean_files = "⌧ Clean temporary files"


class TerragruntOperations:
    """
    Class for Terragrunt operations.
    """

    def __init__(self, velez):
        self.velez = velez
        if not self.velez.check_terragrunt():
            input("Press Enter to return to the main menu...")
            self.velez.main_menu()
        self.root_hcl = os.getenv('VELEZ_TG_ROOT_HCL', 'root.hcl')  # Root Terragrunt config file
        if not os.path.exists(self.root_hcl):
            print(f"Root Terragrunt config file {self.root_hcl} not found.")
            input("Press Enter to return to the main menu...")
            self.velez.main_menu()
        self.temp_config = os.getenv('VELEZ_TG_TEMP_CONFIG',
                                     '/tmp/terragrunt_rendered.json')  # Temporary file to store rendered config
        self.use_s3_backend = False  # If S3 backend is used, will be updated for each module separately
        self.use_dynamodb_locks = False  # If DynamoDB locks are used, will be updated for each module separately
        self.dynamodb_table = None  # DynamoDB table name, will be updated for each module separately
        self.dynamodb_lockid = None  # DynamoDB lock ID, will be updated for each module separately
        self.s3_bucket_name = None  # S3 backend bucket name, will be updated for each module separately
        self.s3_state_key = None  # S3 tfstate key, will be updated for each module separately
        self.s3_state_path = None  # Full S3 tfstate path, will be updated for each module separately
        self.terragrunt_version = self.get_terragrunt_version(quiet=True)
        self.terraform_version = self.get_terraform_version(quiet=True)
        self.opentofu_version = self.get_opentofu_version(quiet=True)
        self.module = None  # Will be updated for each module separately

    @staticmethod
    def list_folders_to_ignore() -> list:
        """
        List of folders to ignore when listing folders.
        :return: list
        """
        return ['.terragrunt-cache', '.terraform-plugin-cache']

    @staticmethod
    def list_not_wait_for() -> list:
        """
        List of commands that can be run without waiting for user input.
        :return: list
        """
        return ['render-json', 'init']

    @staticmethod
    def get_terraform_version(quiet: bool = False) -> str:
        """
        Check Terraform version.
        :param quiet: if True, suppress output and errors
        :return: Terraform version as a string
        """
        terraform_version = ''
        try:
            output, err = run_command(['terraform', '-version'], quiet=quiet)
            if output:
                first_line = output.splitlines()[0]
                match = re.search(r'Terraform v(\d+\.\d+\.\d+)', first_line)
                if match:
                    terraform_version = match.group(1)
                    if not quiet:
                        print(f'Terraform version: {terraform_version}')
        except Exception as e:
            if not quiet:
                print(f'Error checking Terraform version: {e}')
        return terraform_version

    @staticmethod
    def get_opentofu_version(quiet: bool = False) -> str:
        """
        Check OpenTofu version.
        :param quiet: if True, suppress output and errors
        :return: OpenTofu version as a string
        """
        opentofu_version = ''
        try:
            output, err = run_command(['tofu', '--version'], quiet=quiet)
            if output:
                first_line = output.splitlines()[0]
                match = re.search(r'OpenTofu v(\d+\.\d+\.\d+)', first_line)
                if match:
                    opentofu_version = match.group(1)
                    if not quiet:
                        print(f'OpenTofu version: {opentofu_version}')
        except Exception as e:
            if not quiet:
                print(f'Error checking OpenTofu version: {e}')
        return opentofu_version

    @staticmethod
    def get_terragrunt_version(quiet: bool = False) -> str:
        """
        Check Terragrunt version.
        :param quiet: if True, suppress output and errors
        :return: Terragrunt version as a string
        """
        terragrunt_version = ''
        try:
            output, err = run_command(['terragrunt', '-v'], quiet=quiet)
            if output:
                first_line = output.splitlines()[0]
                match = re.search(r'terragrunt version (\d+\.\d+\.\d+)', first_line)
                if match:
                    terragrunt_version = match.group(1)
                    if not quiet:
                        print(f'Terragrunt version: {terragrunt_version}')
        except Exception as e:
            if not quiet:
                print(f'Error checking Terragrunt version: {e}')
        return terragrunt_version

    def list_folders(self, base_dir: str = None) -> list:
        """
        List all folders in the base directory.
        :param base_dir: base directory to list folders from
        :return: list
        """
        if base_dir is None:
            base_dir = self.velez.base_dir

        folders = []
        for item in sorted(os.listdir(base_dir)):
            item_path = os.path.join(base_dir, item)
            if os.path.isdir(item_path) and item not in self.list_folders_to_ignore() and not item.startswith('.'):
                folders.append(item_path)
        return folders

    def folder_menu(self, current_dir: str = None) -> None:
        """
        Display folder menu.
        :param current_dir: current directory
        :return: None
        """
        if current_dir is None:
            current_dir = self.velez.base_dir

        folders = self.list_folders(current_dir)
        if not folders:
            print("No folders found in the current directory.")
            input("Press Enter to return to the previous menu...")
            self.folder_menu(os.path.dirname(current_dir))
            return

        options = []
        for folder in folders:
            if 'terragrunt.hcl' in os.listdir(folder):
                options.append(f"🌟 {os.path.basename(folder)}")
            else:
                options.append(f"📁 {os.path.basename(folder)}")
        options += [str_back, str_exit]

        title = f"Current Directory: {os.path.relpath(current_dir, self.velez.base_dir)}. Choose a folder to explore:"
        option, index = pick(options, title)

        if option == str_back:
            if current_dir == self.velez.base_dir:
                self.velez.main_menu()
            else:
                parent_dir = os.path.dirname(current_dir)
                self.folder_menu(parent_dir)
        elif option == str_exit:
            sys.exit()
        else:
            selected_folder = folders[index]
            if '🌟' in option:
                folder_path = os.path.relpath(selected_folder, self.velez.base_dir)
                self.update_self(str(folder_path))
                self.action_menu()
            else:
                self.folder_menu(selected_folder)

    def action_menu(self) -> None:
        """
        Display Terragrunt actions menu.
        :return: None
        """
        options = [
            str_plan,
            str_apply,
            str_import,
            str_destroy,
            str_output,
            str_init,
            str_validate,
            str_refresh,
            str_taint_menu,
            str_clean_files,
        ]
        if self.velez.use_s3_backend and self.velez.use_dynamodb_locks:
            options += [
                str_state_menu,
                str_module_menu,
                str_lock_menu,
            ]
        options += [
            str_back,
            str_exit
        ]
        title = f"Current Module: {self.module}. Choose an action:"
        option, index = pick(options, title)

        if option == str_back:
            self.folder_menu(os.path.dirname(self.module))
        elif option == str_exit:
            sys.exit()
        elif option == str_plan:
            self.plan_action()
            self.action_menu()
        elif option == str_apply:
            self.apply_action()
            self.action_menu()
        elif option == str_import:
            self.import_action()
            self.action_menu()
        elif option == str_destroy:
            self.destroy_action()
            self.action_menu()
        elif option == str_output:
            self.output_action()
            self.action_menu()
        elif option == str_init:
            self.init_action()
            self.action_menu()
        elif option == str_validate:
            self.validate_action()
            self.action_menu()
        elif option == str_refresh:
            self.refresh_action()
            self.action_menu()
        elif option == str_clean_files:
            if self.velez.file_ops is None:
                self.velez.file_ops = FileOperations(self.velez)
            self.velez.file_ops.clean_files()
            self.action_menu()
        elif option == str_state_menu:
            self.state_menu()
        elif option == str_module_menu:
            self.module_menu()
        elif option == str_taint_menu:
            self.taint_menu()
        elif option == str_lock_menu:
            self.lock_menu()

    def plan_action(self) -> None:
        """
        Terraform Plan action.
        :return: None
        """
        resource = input("Enter the target to plan (e.g., module.resource; will run the whole module if empty): ")
        if resource:
            self.run_terragrunt(['run', 'plan', '-target', resource])
        else:
            self.run_terragrunt(['run', 'plan'])

    def apply_action(self) -> None:
        """
        Terraform Apply action.
        :return: None
        """
        resource = input("Enter the target to apply (e.g., module.resource; will run the whole module if empty): ")
        if resource:
            self.run_terragrunt(['run', 'apply', '-target', resource])
        else:
            self.run_terragrunt(['run', 'apply'])

    def import_action(self) -> None:
        """
        Terraform Import action.
        :return: None
        """
        resource = input("Enter the address of the resource to import (e.g., aws_instance.example): ")
        resource_id = input("Enter the resource ID to import (e.g., i-12345678): ")
        if resource and resource_id:
            self.run_terragrunt(['run', 'import', resource, resource_id])

    def destroy_action(self) -> None:
        """
        Terraform Destroy action.
        :return: None
        """
        resource = input(
            "Enter the target to destroy (e.g., module.resource; will run the whole module if empty): ")
        if resource:
            self.run_terragrunt(['run', 'destroy', '-target', resource])
        else:
            self.run_terragrunt(['run', 'destroy'])

    def output_action(self) -> None:
        """
        Terraform Output action.
        :return: None
        """
        variable = input("Enter the output variable to show (e.g., my_output; will show all if empty): ")
        self.run_terragrunt(['run', 'output', variable])

    def init_action(self) -> None:
        """
        Terraform Init action.
        :return: None
        """
        self.run_terragrunt(['run', 'init'])

    def validate_action(self) -> None:
        """
        Terraform Validate action.
        :return: None
        """
        self.run_terragrunt(['run', 'validate'])

    def refresh_action(self) -> None:
        """
        Terraform Refresh action.
        :return: None
        """
        self.run_terragrunt(['run', 'refresh'])

    def state_menu(self) -> None:
        """
        Display state menu.
        :return: None
        """
        state_options = [
            str_state_list,
            str_state_move,
            str_state_rm,
            str_state_show,
            str_state_pull,
            str_state_push,
            str_back,
            str_exit
        ]
        state_title = f"Current Module: {self.module}. Choose a state operation:"
        state_option, state_index = pick(state_options, state_title)
        if state_option == str_back:
            self.action_menu()
        elif state_option == str_exit:
            sys.exit()
        elif state_option == str_state_list:
            resource = input("Enter the address of the resource to list (e.g., module.example): ")
            self.run_terragrunt(['run', 'state', 'list', resource])
            self.action_menu()
        elif state_option == str_state_move:
            source = input("Enter the source address of the resource to move (e.g., module.one.aws_instance.this): ")
            destination = input(
                "Enter the destination address of the resource to move (e.g., module.two.aws_instance.this): ")
            self.run_terragrunt(['run', 'state', 'mv', source, destination])
            self.action_menu()
        elif state_option == str_state_rm:
            resource = input("Enter the address of the resource to remove (e.g., aws_instance.example): ")
            self.run_terragrunt(['run', 'state', 'rm', resource])
            self.action_menu()
        elif state_option == str_state_show:
            resource = input("Enter the address of the resource to show (e.g., aws_instance.example): ")
            self.run_terragrunt(['run', 'state', 'show', resource])
            self.action_menu()
        elif state_option == str_state_pull:
            self.run_terragrunt(['run', 'state', 'pull'])
            self.action_menu()
        elif state_option == str_state_push:
            self.run_terragrunt(['run', 'state', 'push'])
            self.action_menu()

    def module_menu(self) -> None:
        """
        Display module menu.
        :return: None
        """
        module_options = [
            str_module_move if self.velez.use_s3_backend and self.velez.use_dynamodb_locks else None,
            str_module_destroy if self.velez.use_s3_backend and self.velez.use_dynamodb_locks else None,
            str_module_destroy_backend if self.velez.use_s3_backend and self.velez.use_dynamodb_locks else None,
            str_back,
            str_exit
        ]
        module_options = [i for i in module_options if i is not None or i != '']
        module_title = f"Current Module: {self.module}. Choose a module operation:"
        module_option, module_index = pick(module_options, module_title)
        if module_option == str_back:
            self.action_menu()
        elif module_option == str_exit:
            sys.exit()
        elif module_option == str_module_move:
            self.module_move_action()
        elif module_option == str_module_destroy:
            self.module_destroy_action()
        elif module_option == str_module_destroy_backend:
            self.module_destroy_backend_action()

    def taint_menu(self) -> None:
        """
        Display Terraform taint menu.
        :return: None
        """
        taint_options = [
            str_untaint,
            str_taint,
            str_back,
            str_exit
        ]
        taint_title = f"Current Module: {self.module}. Choose a taint operation"
        taint_option, taint_index = pick(taint_options, taint_title)
        if taint_option == str_back:
            self.action_menu()
        elif taint_option == str_exit:
            sys.exit()
        elif taint_option == str_taint:
            self.taint_action()
        elif taint_option == str_untaint:
            self.untaint_action()

    def lock_menu(self) -> None:
        """
        Display Terraform lock menu.
        :return: None
        """
        lock_options = [
            str_lock_info,
            str_unlock,
            str_back,
            str_exit
        ]
        lock_title = f"Current Module: {self.module}. Choose a lock operation:"
        lock_option, lock_index = pick(lock_options, lock_title)
        if lock_option == str_back:
            self.action_menu()
        elif lock_option == str_exit:
            sys.exit()
        elif lock_option == str_unlock:
            self.unlock_action()
        elif lock_option == str_lock_info:
            self.lock_info_action()

    def module_move_action(self) -> None:
        """
        Move Terragrunt module action.
        :return: None
        """
        destination = input("Enter the destination path (e.g., aws/prod): ")

        if self.velez.use_dynamodb_locks and self.velez.use_s3_backend:
            print("Using DynamoDB lock table: ", self.velez.dynamodb_table)
            print("Using DynamoDB LockID: ", self.velez.dynamodb_lockid)
            print("Using S3 source path: ", self.velez.s3_state_path)
            destination_key = f'{self.velez.s3_state_key.replace(self.module, destination)}'
            s3_destination = f's3://{self.velez.s3_bucket_name}/{destination_key}'
            print("Using S3 destination path: ", s3_destination)
        else:
            print("DynamoDB Locks and S3 Backend are not enabled.")
            input("Press Enter to return to previous menu...")
            self.action_menu()

        print("Moving source files...")
        os.makedirs(destination, exist_ok=True)
        for file_name in os.listdir(self.module):
            full_file_name = os.path.join(self.module, file_name)
            if os.path.isfile(full_file_name):
                os.rename(full_file_name, os.path.join(destination, file_name))

        if self.velez.use_dynamodb_locks:
            self.dynamodb_delete_lock()

        print("Moving state files on S3...")
        try:
            s3 = boto3.client('s3')
            s3_source_bucket, s3_source_prefix = self.velez.s3_state_path.replace("s3://", "").split("/", 1)
            s3_destination_bucket, s3_destination_prefix = s3_destination.replace("s3://", "").split("/", 1)

            paginator = s3.get_paginator('list_objects_v2')
            for page in paginator.paginate(Bucket=s3_source_bucket, Prefix=s3_source_prefix):
                for obj in page.get('Contents', []):
                    copy_source = {'Bucket': s3_source_bucket, 'Key': obj['Key']}
                    destination_key = obj['Key'].replace(s3_source_prefix, s3_destination_prefix, 1)
                    s3.copy_object(CopySource=copy_source, Bucket=s3_destination_bucket, Key=destination_key)
                    s3.delete_object(Bucket=s3_source_bucket, Key=obj['Key'])
        except Exception as e:
            print(f"An error occurred: {e}")

        print("Adding moved files to git...")
        run_command(['git', 'add', destination])

        # Jump to destination
        self.module = destination
        self.action_menu()

    def module_destroy_action(self) -> None:
        """
        Destroy Terragrunt module action.
        :return: None
        """
        if self.velez.use_dynamodb_locks and self.velez.use_s3_backend:
            print("Using DynamoDB lock table: ", self.velez.dynamodb_table)
            print("Using DynamoDB LockID: ", self.velez.dynamodb_lockid)
            print("Using S3 path: ", self.velez.s3_state_path)
        else:
            print("DynamoDB Locks and S3 Backend are not enabled.")
            input("Press Enter to return to previous menu...")
            self.action_menu()

        print("Destroying resources...")
        self.run_terragrunt(['run', 'destroy'])
        self.dynamodb_delete_lock()
        self.s3_delete_state()

        print("Deleting module folder...")
        try:
            os.rmdir(self.module)
        except Exception as e:
            print(f"An error occurred: {e}")
        # Jump to parent folder
        self.folder_menu(os.path.dirname(self.module))

    def module_destroy_backend_action(self) -> None:
        """
        Destroy Terragrunt module backend action.
        :return: None
        """
        if self.velez.use_dynamodb_locks and self.velez.use_s3_backend:
            print("Using DynamoDB lock table: ", self.velez.dynamodb_table)
            print("Using DynamoDB LockID: ", self.velez.dynamodb_lockid)
            s3_state = f"s3://{self.velez.s3_bucket_name}/{self.velez.s3_state_key}"
            print("Using S3 path: ", s3_state)
        else:
            print("DynamoDB Locks and S3 Backend are not enabled.")
            input("Press Enter to return to previous menu...")
            self.action_menu()

        self.dynamodb_delete_lock()
        self.s3_delete_state()
        self.action_menu()

    def dynamodb_delete_lock(self) -> None:
        """
        Delete LockID from DynamoDB.
        :return: None
        """
        print("Deleting LockID from DynamoDB...")
        try:
            dynamodb = boto3.client('dynamodb')
            dynamodb.delete_item(
                TableName=self.velez.dynamodb_name,
                Key={'LockID': {'S': self.velez.dynamodb_lockid}}
            )
        except Exception as e:
            print(f"An error occurred: {e}")

    def dynamodb_show_lock(self) -> None:
        """
        Show LockID from DynamoDB.
        :return: None
        """
        print("Showing LockID from DynamoDB...")
        try:
            dynamodb = boto3.client('dynamodb')
            response = dynamodb.get_item(
                TableName=self.velez.dynamodb_name,
                Key={'LockID': {'S': self.velez.dynamodb_lockid}}
            )
            print(response)
        except Exception as e:
            print(f"An error occurred: {e}")

    def s3_delete_state(self) -> None:
        """
        Delete state file on S3.
        :return: None
        """
        print("Deleting state file on S3...")
        try:
            s3 = boto3.client('s3')
            s3.delete_object(Bucket=self.velez.s3_bucket_name, Key=self.velez.s3_state_key)
        except Exception as e:
            print(f"An error occurred: {e}")

    def untaint_action(self) -> None:
        """
        Untaint a resource.
        :return: None
        """
        address = input("Enter the address of the resource to untaint (e.g., aws_instance.example): ")
        self.run_terragrunt(['run', 'untaint', address])
        self.action_menu()

    def taint_action(self) -> None:
        """
        Taint a resource.
        :return: None
        """
        address = input("Enter the address of the resource to taint (e.g., aws_instance.example): ")
        self.run_terragrunt(['run', 'taint', address])
        self.action_menu()

    def lock_info_action(self) -> None:
        """
        Show lock info.
        :return: None
        """
        self.dynamodb_show_lock()
        self.action_menu()

    def unlock_action(self) -> None:
        """
        Unlock the state.
        :return: None
        """
        self.run_terragrunt(['run', 'force-unlock'])
        self.action_menu()

    def run_terragrunt(self, arguments: list, quiet: bool = False) -> None:
        """
        Run Terragrunt command.
        :param arguments: list of arguments to pass to Terragrunt
        :param quiet: if True, suppress output and errors
        :return: None
        """
        args = [i for i in arguments if i is not None or i != '']
        # Building the full command
        command = ['terragrunt'] + args
        # check if cli-redesign is possible
        if self.velez.terragrunt_version >= '0.73.0':
            if 'run' in args:
                command += ['--tf-forward-stdout', '--experiment', 'cli-redesign']
        if self.module:
            command += ['--working-dir', f'{self.module}']
        out, err = run_command(command, quiet=quiet)
        if not any(i in args for i in self.list_not_wait_for()):
            input("Press Enter when ready to continue...")

    def load_terragrunt_config(self) -> dict:
        """
        Load Terragrunt module configuration from running Terragrunt.
        :return: dict
        """
        run_command(['terragrunt', 'render-json', '--out', self.velez.temp_config], quiet=True)
        if self.velez.file_ops is None:
            self.velez.file_ops = FileOperations(self.velez)
        return self.velez.file_ops.load_json_file(self.velez.temp_config)

    def update_self(self, module_path: str) -> None:
        """
        Update class variables with new module path.
        :param module_path: path to the module
        :return: None
        """
        self.module = module_path
        config = self.load_terragrunt_config()
        if 'remote_state' in config:
            remote_state = config['remote_state']
            if remote_state['backend'] == 's3':
                self.velez.use_s3_backend = True
                if 'config' in remote_state:
                    config = remote_state['config']
                    if 'dynamodb_table' in config:
                        self.velez.use_dynamodb_locks = True
                        self.velez.dynamodb_table = config['dynamodb_table']
                    if 'bucket' in config:
                        self.velez.s3_bucket_name = config['bucket']
                    if 'key' in config:
                        self.velez.s3_state_key = config['key']
                    if self.velez.dynamodb_table and self.velez.s3_bucket_name and self.velez.s3_state_key:
                        self.velez.dynamodb_lockid = f"{self.velez.s3_bucket_name}/{self.velez.s3_state_key}-md5"
                        self.velez.s3_state_path = f"s3://{self.velez.s3_bucket_name}/{self.velez.s3_state_key}"
