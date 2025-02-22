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


def run_command(command: list[str]) -> tuple:
    """
    Run a command.
    :param command: command to run
    :return: tuple with stdout and stderr
    """
    print(f"Running command: {command}")
    try:
        cmd = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True, universal_newlines=True)
        out, err = cmd.communicate()
        return out, err
    except Exception as e:
        print(f"Error running command: {e}")
        return None, e
