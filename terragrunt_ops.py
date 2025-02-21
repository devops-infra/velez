import os
import subprocess

import boto3

from pick import pick

menu_plan = "📋 Plan"
menu_apply = "✅ Apply"
menu_import = "📎 Import"
menu_destroy = "💣 Destroy"
menu_state = "📦 State operations"
menu_module = "📦 Module operations"
menu_taint = "🚫 Taint"
menu_untaint = "♻️ Untaint"
menu_unlock = "🔓 Unlock"
menu_output = "📤 Output"
menu_init = "🚀 Initialize"
menu_validate = "☑️ Validate"
menu_refresh = "🔄 Refresh"
state_list = "📄 List"
state_move = "📦 Move"
state_rm = "🗑️ Remove"
state_show = "🔍 Show"
state_pull = "⤵️ Pull"
state_push = "⤴ Push"
module_move = "↔️ Move module"
module_destroy_backend = "⌫ Destroy backend"
module_destroy = "🗑️ Destroy module"


def list_folders_to_ignore():
    return ['.terragrunt-cache', '.terraform-plugin-cache']


class TerragruntOperations:
    def __init__(self, velez):
        self.velez = velez

    def list_folders(self, base_dir=None):
        if base_dir is None:
            base_dir = self.velez.base_dir

        folders = []
        for item in sorted(os.listdir(base_dir)):
            item_path = os.path.join(base_dir, item)
            if os.path.isdir(item_path) and item not in list_folders_to_ignore():
                folders.append(item_path)
        return folders

    def list_modules(self, folder):
        modules = []
        for root, _, files in os.walk(folder):
            if 'terragrunt.hcl' in files:
                modules.append(root)
        return modules

    def folder_menu(self, current_dir=None):
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

        options += [self.velez.menu_back, self.velez.menu_exit]

        title = f"Choose a folder to explore. Current Directory: {os.path.relpath(current_dir, self.velez.base_dir)}"
        option, index = pick(options, title)

        if option == self.velez.menu_back:
            if current_dir == self.velez.base_dir:
                self.velez.main_menu()
            else:
                parent_dir = os.path.dirname(current_dir)
                self.folder_menu(parent_dir)
        elif option == self.velez.menu_exit:
            exit()
        else:
            selected_folder = folders[index]
            if '🌟' in option:
                self.action_menu(selected_folder)
            else:
                self.folder_menu(selected_folder)

    def action_menu(self, module):
        options = [
                      menu_plan,
                      menu_apply,
                      menu_import,
                      menu_destroy,
                      menu_state,
                      menu_taint,
                      menu_untaint,
                      menu_unlock,
                      menu_output,
                      menu_init,
                      menu_validate,
                      menu_refresh
                  ] + [self.velez.menu_back, self.velez.menu_exit]
        title = f"Choose an action. Current Module: {os.path.relpath(module, self.velez.base_dir)}:"
        option, index = pick(options, title)

        if option == self.velez.menu_back:
            self.folder_menu(os.path.dirname(module))
        elif option == self.velez.menu_exit:
            exit()

        # Plan
        elif option == menu_plan:
            resource = input("Enter the target to plan (e.g., module.resource; will run the whole module if empty): ")
            if resource:
                self.execute_terragrunt(module, ['plan', '-target', resource])
                self.action_menu(module)
            else:
                self.execute_terragrunt(module, ['plan'])
                self.action_menu(module)

        # Apply
        elif option == menu_apply:
            resource = input("Enter the target to apply (e.g., module.resource; will run the whole module if empty): ")
            if resource:
                self.execute_terragrunt(module, ['apply', '-target', resource])
                self.action_menu(module)
            else:
                self.execute_terragrunt(module, ['apply'])
                self.action_menu(module)

        # Import
        elif option == menu_import:
            resource = input("Enter the address of the resource to import (e.g., aws_instance.example): ")
            resource_id = input("Enter the resource ID to import (e.g., i-12345678): ")
            if resource and resource_id:
                self.execute_terragrunt(module, ['import', resource, resource_id])
                self.action_menu(module)

        # Destroy
        elif option == menu_destroy:
            resource = input(
                "Enter the target to destroy (e.g., module.resource; will run the whole module if empty): ")
            if resource:
                self.execute_terragrunt(module, ['destroy', '-target', resource])
                self.action_menu(module)
            else:
                self.execute_terragrunt(module, ['destroy'])
                self.action_menu(module)

        # State operations
        elif option == menu_state:
            state_options = [
                state_list,
                state_move,
                state_rm,
                state_show,
                state_pull,
                state_push,
                self.velez.menu_back,
                self.velez.menu_exit
            ]
            state_title = f"Choose a state operation. Current Module: {os.path.relpath(module, self.velez.base_dir)}:"
            state_option, state_index = pick(state_options, state_title)
            if state_option == self.velez.menu_back:
                self.action_menu(module)
            elif state_option == self.velez.menu_exit:
                exit()
            elif state_option == state_list:
                resource = input("Enter the address of the resource to list (e.g., module.example): ")
                self.execute_terragrunt(module, ['state', 'list', resource])
                self.action_menu(module)
            elif state_option == state_move:
                source = input("Enter the source address of the resource to move (e.g., aws_instance.example): ")
                destination = input(
                    "Enter the destination address of the resource to move (e.g., aws_instance.example): ")
                self.execute_terragrunt(module, ['state', 'mv', source, destination])
                self.action_menu(module)
            elif state_option == state_rm:
                resource = input("Enter the address of the resource to remove (e.g., aws_instance.example): ")
                self.execute_terragrunt(module, ['state', 'rm', resource])
                self.action_menu(module)
            elif state_option == state_show:
                resource = input("Enter the address of the resource to show (e.g., aws_instance.example): ")
                self.execute_terragrunt(module, ['state', 'show', resource])
                self.action_menu(module)
            elif state_option == state_pull:
                self.execute_terragrunt(module, ['state', 'pull'])
                self.action_menu(module)
            elif state_option == state_push:
                self.execute_terragrunt(module, ['state', 'push'])
                self.action_menu(module)

        # Module operations
        elif option == menu_module:
            module_options = [
                module_move,
                module_destroy,
                module_destroy_backend,
                self.velez.menu_back,
                self.velez.menu_exit
            ]
            module_title = f"Choose a module operation. Current Module: {os.path.relpath(module, self.velez.base_dir)}:"
            module_option, module_index = pick(module_options, module_title)
            if module_option == self.velez.menu_back:
                self.action_menu(module)
            elif module_option == self.velez.menu_exit:
                exit()

            # Move module
            elif module_option == module_move:
                destination = input("Enter the destination path (e.g., aws/prod): ")
                dynamodb_name = input("Enter the DynamoDB lock table name (e.g., my_table): ")
                dynamodb_lockid = input("Enter the DynamoDB LockID (e.g., my-terragrunt/aws/dev/account/terraform.tfstate-md5): ")
                s3_source = input("Enter the S3 source path (e.g., s3://my-terragrunt/aws/dev/account): ")
                s3_destination = input("Enter the S3 destination path (e.g., s3://my-terragrunt/aws/prod): ")

                print("Moving source files...")
                os.makedirs(destination, exist_ok=True)
                for file_name in os.listdir(module):
                    full_file_name = os.path.join(module, file_name)
                    if os.path.isfile(full_file_name):
                        os.rename(full_file_name, os.path.join(destination, file_name))

                print("Deleting LockID from DynamoDB...")
                dynamodb = boto3.client('dynamodb')
                dynamodb.delete_item(
                    TableName=dynamodb_name,
                    Key={'LockID': {'S': dynamodb_lockid}}
                )

                print("Moving state files on S3...")
                s3 = boto3.client('s3')
                s3_source_bucket, s3_source_prefix = s3_source.replace("s3://", "").split("/", 1)
                s3_destination_bucket, s3_destination_prefix = s3_destination.replace("s3://", "").split("/", 1)

                paginator = s3.get_paginator('list_objects_v2')
                for page in paginator.paginate(Bucket=s3_source_bucket, Prefix=s3_source_prefix):
                    for obj in page.get('Contents', []):
                        copy_source = {'Bucket': s3_source_bucket, 'Key': obj['Key']}
                        destination_key = obj['Key'].replace(s3_source_prefix, s3_destination_prefix, 1)
                        s3.copy_object(CopySource=copy_source, Bucket=s3_destination_bucket, Key=destination_key)
                        s3.delete_object(Bucket=s3_source_bucket, Key=obj['Key'])

                print("Adding moved files to git...")
                subprocess.run(['git', 'add', destination])

                self.action_menu(destination)

            # Destroy whole module
            elif module_option == module_destroy:
                dynamodb_name = input("Enter the DynamoDB lock table name (e.g., my_table): ")
                dynamodb_lockid = input("Enter the DynamoDB LockID (e.g., my-terragrunt/aws/dev/account/terraform.tfstate-md5): ")
                s3_state = input("Enter the S3 state path (e.g., s3://my-terragrunt/aws/dev/account): ")
                print("Destroying resources...")
                self.execute_terragrunt(module, ['destroy'])

                print("Deleting LockID from DynamoDB...")
                dynamodb = boto3.client('dynamodb')
                dynamodb.delete_item(
                    TableName=dynamodb_name,
                    Key={'LockID': {'S': dynamodb_lockid}}
                )

                print("Deleting state files on S3...")
                s3 = boto3.client('s3')
                s3_bucket, s3_prefix = s3_state.replace("s3://", "").split("/", 1)
                paginator = s3.get_paginator('list_objects_v2')
                for page in paginator.paginate(Bucket=s3_bucket, Prefix=s3_prefix):
                    for obj in page.get('Contents', []):
                        s3.delete_object(Bucket=s3_bucket, Key=obj['Key'])

                print("Deleting module folder...")
                os.rmdir(module)

                self.action_menu(os.path.dirname(module))

            # Destroy backend for the module
            elif module_option == module_destroy_backend:
                dynamodb_name = input("Enter the DynamoDB lock table name (e.g., my_table): ")
                dynamodb_lockid = input("Enter the DynamoDB LockID (e.g., my-terragrunt/aws/dev/account/terraform.tfstate-md5): ")
                s3_state = input("Enter the S3 state path (e.g., s3://my-terragrunt/aws/dev/account): ")

                print("Deleting LockID from DynamoDB...")
                dynamodb = boto3.client('dynamodb')
                dynamodb.delete_item(
                    TableName=dynamodb_name,
                    Key={'LockID': {'S': dynamodb_lockid}}
                )

                print("Deleting state files on S3...")
                s3 = boto3.client('s3')
                s3_bucket, s3_prefix = s3_state.replace("s3://", "").split("/", 1)
                paginator = s3.get_paginator('list_objects_v2')
                for page in paginator.paginate(Bucket=s3_bucket, Prefix=s3_prefix):
                    for obj in page.get('Contents', []):
                        s3.delete_object(Bucket=s3_bucket, Key=obj['Key'])

                self.action_menu(module)

        # Taint
        elif option == menu_taint:
            address = input("Enter the address of the resource to taint (e.g., aws_instance.example): ")
            self.execute_terragrunt(module, ['taint', address])
            self.action_menu(module)

        # Untaint
        elif option == menu_untaint:
            address = input("Enter the address of the resource to untaint (e.g., aws_instance.example): ")
            self.execute_terragrunt(module, ['untaint', address])
            self.action_menu(module)

        # Unlock
        elif option == menu_unlock:
            self.execute_terragrunt(module, ['force-unlock'])
            self.action_menu(module)

        # Output
        elif option == menu_output:
            variable = input("Enter the output variable to show (e.g., my_output; will show all if empty): ")
            self.execute_terragrunt(module, ['output', variable])
            self.action_menu(module)

        # Initialize
        elif option == menu_init:
            self.execute_terragrunt(module, ['init'])
            self.action_menu(module)

        # Validate
        elif option == menu_validate:
            self.execute_terragrunt(module, ['validate'])
            self.action_menu(module)

        # Refresh
        elif option == menu_refresh:
            self.execute_terragrunt(module, ['refresh'])
            self.action_menu(module)

    def execute_terragrunt(self, module, arguments):
        args = [i for i in arguments if i is not None or i != '']
        module = os.path.relpath(module, self.velez.base_dir)
        # TODO: echo to debug
        command = ['echo', 'terragrunt', '--terragrunt-forward-tf-stdout'] + args + ['--terragrunt-working-dir', f'{module}']
        print(f"Running command: {command}")
        try:
            result = subprocess.run(
                command,
                # cwd=module,
                capture_output=True,
                text=True
            )
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
        except Exception as e:
            print(f"An error occurred: {e}")
        input("Press Enter to return to the previous menu...")
