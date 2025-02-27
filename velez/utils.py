import shutil
import subprocess

str_back = "⏎ Back"
str_exit = "⏏︎ Exit"


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
