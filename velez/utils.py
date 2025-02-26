import re
import shutil
import subprocess


str_back = "🔙 Back"
str_exit = "❌ Exit"
str_terragrunt_menu = "🌟 Run Terragrunt"
str_file_menu = "🗃️  File operations"
str_plan = "📋 Plan"
str_apply = "✅ Apply"
str_import = "📎 Import"
str_destroy = "💣 Destroy"
str_output = "📤 Output"
str_init = "🚀 Initialize"
str_validate = "👌 Validate"
str_refresh = "🔄 Refresh"
str_state_menu = "📁 State operations"
str_state_list = "📄 List"
str_state_move = "📦 Move"
str_state_rm = "🗑️ Remove"
str_state_show = "🔍 Show"
str_state_pull = "↘️️ Pull"
str_state_push = "↗️ Push"
str_module_menu = "📁 Module operations"
str_module_move = "↔️ Move module"
str_module_destroy = "🗑️ Destroy module"
str_module_destroy_backend = "🚮 Destroy backend"
str_taint_menu = "📁 Taint operations"
str_taint = "🚫 Taint"
str_untaint = "♻️ Untaint"
str_lock_menu = "📁 Lock operations"
str_lock_info = "ℹ️ Lock info"
str_unlock = "🔓 Unlock"
str_format_files = "📑 Format HCL files"
str_clean_files = "🧹 Clean temporary files"


def run_command(command: list[str], quiet: bool = False) -> tuple:
    """
    Run a command.
    :param command: command to run
    :param quiet: if True, suppress output and errors
    :return: tuple with stdout and stderr
    """
    # check if command is recognizable by the system
    if not shutil.which(command[0]):
        if not quiet:
            print(f"Error: Command not found: {command[0]}")
            return '', f"Command not found: {command[0]}"
    if not quiet:
        print(f"Running command: {' '.join(command)}")

    try:
        cmd = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        out, err = cmd.communicate()
        if not quiet:
            if out:
                print(out)
            if err:
                print(err)
        return out, err
    except Exception as e:
        if not quiet:
            print(f"\n\nError running command: {e}\n\n")
        return '', str(e)

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

def get_opentofu_version(quiet: bool = False) -> str:
    """
    Check OpenTofu version.
    :param quiet: if True, suppress output and errors
    :return: OpenTofu version as a string
    """
    opentofu_version = ''
    try:
        output, err = run_command(['opentofu', '--version'], quiet=quiet)
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
