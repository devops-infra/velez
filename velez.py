import argparse
import os

from pick import pick

from terragrunt_ops import TerragruntOperations


class Velez:
    menu_back = "🔙 Back"
    menu_exit = "🚪 Exit"
    menu_terragrunt = "🌟 Run Terragrunt"

    def __init__(self, base_dir=None):
        self.base_dir = base_dir if base_dir else os.getcwd()
        self.terragrunt_ops = TerragruntOperations(self)

    def main_menu(self):
        title = "Choose a service:"
        options = [
            self.menu_terragrunt,
            self.menu_exit]
        option, index = pick(options, title)

        if option == self.menu_terragrunt:
            self.terragrunt_ops.folder_menu()
        elif option == self.menu_exit:
            exit()

        self.main_menu()

    def run(self, terragrunt=False, **kwargs):
        if terragrunt and kwargs.get('pos_args'):
            self.terragrunt_ops.execute_terragrunt(module=self.base_dir, arguments=kwargs.get('pos_args'))
        elif terragrunt:
            self.terragrunt_ops.folder_menu()
        else:
            self.main_menu()


def main():
    parser = argparse.ArgumentParser(description='Velez CLI')
    parser.add_argument('--terragrunt', '-tg', action='store_true', help='Run Terragrunt operations')
    parser.add_argument('pos_args', nargs=argparse.REMAINDER, help='Arguments to pass further')

    args = parser.parse_args()

    framework = Velez()
    framework.run(terragrunt=args.terragrunt, pos_args=args.pos_args)


if __name__ == "__main__":
    main()
