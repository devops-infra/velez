import shutil
from datetime import datetime
import subprocess

STR_BACK = "⏮️  BACK"
STR_EXIT = "📛 EXIT"


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

def get_date_str(date: str | datetime) -> str:
    """
    Convert date and time to a string.
    :param date: datetime object or string with date and time in format "%Y-%m-%dT%H:%M:%S.%fZ"
    :return: date and time in format "YYYY-MM-DD HH:MM:SS"
    """
    if isinstance(date, datetime):
        return date.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(date, str):
        if date == "Never":
            return date
        return get_datetime(date).strftime("%Y-%m-%d %H:%M:%S")
    else:
        return str(date)

def get_datetime(date: str) -> datetime:
    """
    Convert date and time with a million parts of seconds to a datetime object.
    :return: datetime object
    """
    if date.endswith('Z'):
        date = date[:-1]
    if '.' in date:
        milliseconds = date.split('.')[1][:3]
        date = date.split('.')[0] + '.' + milliseconds
        try:
            return datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f")
        except ValueError:
            raise
    else:
        try:
            return datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            raise

def print_markdown_table(header: str, rows: list[list[str]]) -> None:
    """
    Print a formatted markdown table.
    :param header: List of column headers, as a string
    :param rows: List of rows, where each row is a list of strings
    :return: None
    """
    header_list = header.split(" | ")

    # Calculate the maximum width of each column
    column_widths = [len(col) for col in header_list]
    for row in rows:
        for i, cell in enumerate(row):
            column_widths[i] = max(column_widths[i], len(cell))

    # Create a format string for each row
    row_format = "| " + " | ".join(f"{{:<{width}}}" for width in column_widths) + " |"

    # Print the header
    print(row_format.format(*header_list))
    print("|" + "|".join("-" * (width + 2) for width in column_widths) + "|")

    # Print each row
    for row in rows:
        print(row_format.format(*row))

def bytes_to_human_readable(size: int) -> str:
    """
    Convert a number of bytes to a human-readable string with the largest unit.
    :param size: Number of bytes
    :return: Human-readable string with up to 2 decimal points
    """
    units = ["B", "kB", "MB", "GB", "TB", "PB"]
    unit_index = 0

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    return f"{size:.2f} {units[unit_index]}"
