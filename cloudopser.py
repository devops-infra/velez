import os
import subprocess
import argparse
from pick import pick

class CloudOpser:
    menu_back = '🔙 Back'
    menu_exit = '🚪 Exit'
    menu_terragrunt = '🌟 Run Terragrunt'
    menu_apply = "✅ Apply the whole module"
    menu_apply_target = "📌 Apply only a specific target"
    menu_plan = "📋 Plan the whole module"
    menu_plan_target = "📝 Plan only a specific target"
    menu_import = "📎 Import a resource to the state"
    menu_remove = "🚫 Remove a resource from the state"
    menu_unlock = "🔓 Unlock module"
    menu_destroy = "💣 Destroy the whole module"

    def __init__(self, base_dir=None):
        self.base_dir = base_dir if base_dir else os.getcwd()

    def list_services(self):
        return [
            self.menu_terragrunt
        ]

    def list_folders(self, base_dir=None):
        if base_dir is None:
            base_dir = self.base_dir

        folders = []
        for item in os.listdir(base_dir):
            item_path = os.path.join(base_dir, item)
            if os.path.isdir(item_path) and item != '.terragrunt-cache':
                folders.append(item_path)
        return folders

    def list_modules(self, folder):
        modules = []
        for root, _, files in os.walk(folder):
            if 'terragrunt.hcl' in files:
                modules.append(root)
        return modules

    def run_command(self, module, command):
        try:
            result = subprocess.run(
                ['terragrunt', command],
                cwd=module,
                capture_output=True,
                text=True
            )
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
        except Exception as e:
            print(f"An error occurred: {e}")

    def plan(self, module):
        self.run_command(module, 'plan')

    def apply(self, module):
        self.run_command(module, 'apply')

    def destroy(self, module):
        self.run_command(module, 'destroy')

    def main_menu(self):
        title = 'Choose a service:'
        options = self.list_services() + [self.menu_exit]
        option, index = pick(options, title)

        if option == self.menu_terragrunt:
            self.folder_menu()
        elif option == self.menu_exit:
            exit()

        self.main_menu()

    def folder_menu(self, current_dir=None):
        if current_dir is None:
            current_dir = self.base_dir

        folders = self.list_folders(current_dir)
        if not folders:
            print("No folders found in the current directory.")
            input("Press Enter to return to the previous menu...")
            self.folder_menu(os.path.dirname(current_dir))
            return

        options = []
        for folder in folders:
            subfolders = self.list_folders(folder)
            if 'terragrunt.hcl' in os.listdir(folder):
                options.append(f"🌟 {os.path.basename(folder)}")
            else:
                options.append(f"📁 {os.path.basename(folder)}")

        options += [self.menu_back, self.menu_exit]

        title = f'Current Directory: {os.path.relpath(current_dir, self.base_dir)}\nChoose a folder to explore or an option:'
        option, index = pick(options, title)

        if option == self.menu_back:
            if current_dir == self.base_dir:
                self.main_menu()
            else:
                parent_dir = os.path.dirname(current_dir)
                self.folder_menu(parent_dir)
        elif option == self.menu_exit:
            exit()
        else:
            selected_folder = folders[index]
            if '🌟' in option:
                self.action_menu(selected_folder)
            else:
                self.folder_menu(selected_folder)

    def module_menu(self, folder):
        modules = self.list_modules(folder)
        if not modules:
            print("No modules found.")
            input("Press Enter to return to the previous menu...")
            self.folder_menu(os.path.dirname(folder))
            return

        options = []
        for module in modules:
            if 'terragrunt.hcl' in os.listdir(module):
                options.append(f"🌟 {os.path.basename(module)}")

        options += [self.menu_back, self.menu_exit]

        title = f'Current Folder: {os.path.relpath(folder, self.base_dir)}\n\nChoose a module to perform Terragrunt actions or an option:'
        option, index = pick(options, title)

        if option == self.menu_back:
            self.folder_menu(os.path.dirname(folder))
        elif option == self.menu_exit:
            exit()
        else:
            selected_module = modules[index]
            self.action_menu(selected_module)

    def action_menu(self, module):
        options = [self.menu_plan, self.menu_apply, self.menu_destroy, self.menu_back, self.menu_exit]
        title = f'Current Module: {os.path.relpath(module, self.base_dir)}\n\nChoose a Terragrunt action or an option:'
        option, index = pick(options, title)

        if option == self.menu_back:
            self.folder_menu(os.path.dirname(module))
        elif option == self.menu_exit:
            exit()
        elif option == self.menu_plan:
            self.plan(module)
        elif option == self.menu_apply:
            self.apply(module)
        elif option == self.menu_destroy:
            self.destroy(module)

    def run(self, operation=None, module=None):
        if operation and module:
            if operation == 'plan':
                self.plan(module)
            elif operation == 'apply':
                self.apply(module)
            elif operation == 'destroy':
                self.destroy(module)
            else:
                print(f"Unknown operation: {operation}")
        else:
            self.main_menu()

def main():
    parser = argparse.ArgumentParser(description='CloudOpser CLI')
    parser.add_argument('--operation', choices=['plan', 'apply', 'destroy'], help='The Terragrunt operation to perform')
    parser.add_argument('--module', help='The specific module directory to run the operation on')
    parser.add_argument('--base_dir', help='The base directory to start from')

    args = parser.parse_args()

    framework = CloudOpser(base_dir=args.base_dir)
    framework.run(args.operation, args.module)

if __name__ == "__main__":
    main()
