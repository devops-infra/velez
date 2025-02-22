import os
import subprocess
import sys

import boto3
from pick import pick
from velez.file_ops import load_json_file, clean_files
from velez.utils import run_command, str_back, str_exit, str_apply, str_plan, str_import, str_destroy, str_output, \
    str_init, str_validate, str_refresh, str_state_menu, str_module_menu, str_taint_menu, str_lock_menu, str_state_list, \
    str_state_move, str_state_rm, str_state_show, str_state_pull, str_state_push, str_module_move, str_module_destroy, \
    str_module_destroy_backend, str_taint, str_untaint, str_lock_info, str_unlock, str_clean_files


def list_folders_to_ignore() -> list:
    """
    List of folders to ignore when listing folders.
    :return: list
    """
    return ['.terragrunt-cache', '.terraform-plugin-cache']


class TerragruntOperations:
    """
    Class for Terragrunt operations.
    """
    def __init__(self, velez):
        self.module = ''  # Will be updated for each module separately
        self.velez = velez

    def list_folders(self, base_dir: str=None) -> list:
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
            if os.path.isdir(item_path) and item not in list_folders_to_ignore():
                folders.append(item_path)
        return folders

    def folder_menu(self, current_dir: str=None) -> None:
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

        title = f"Choose a folder to explore. Current Directory: {os.path.relpath(current_dir, self.velez.base_dir)}"
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
        title = f"Choose an action. Current Module: {self.module}:"
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
            clean_files()
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
        state_title = f"Choose a state operation. Current Module: {self.module}:"
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
        module_title = f"Choose a module operation. Current Module: {self.module}:"
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
        taint_title = f"Choose a taint operation. Current Module: {self.module}:"
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
        lock_title = f"Choose a lock operation. Current Module: {self.module}:"
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

        self.action_menu(os.path.dirname(self.module))

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

    def run_terragrunt(self, arguments: list) -> None:
        """
        Run Terragrunt command.
        :param arguments: list of arguments to pass to Terragrunt
        :return: None
        """
        # Commands that be run without waiting for user input
        not_wait_for = ['render-json']
        args = [i for i in arguments if i is not None or i != '']
        # Building the full command
        command = ['terragrunt'] + args
        if 'run' in args:
            command += ['--tf-forward-stdout', '--experiment', 'cli-redesign']
        if self.module:
            command += ['--working-dir', f'{self.module}']
        print(f"Running command: {' '.join(command)}")
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True
            )
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
            if not any(i in args for i in not_wait_for):
                input("Press Enter when ready to continue...")
        except Exception as e:
            print(f"An error occurred: {e}")
            input("Press Enter when ready to continue...")

    def load_terragrunt_config(self) -> dict:
        """
        Load Terragrunt module configuration from running Terragrunt.
        :return: dict
        """
        self.run_terragrunt(['render-json', '--out', self.velez.temp_config])
        return load_json_file(self.velez.temp_config)

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
