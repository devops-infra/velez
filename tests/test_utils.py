import subprocess
from unittest.mock import patch, MagicMock

from velez.utils import run_command


@patch('shutil.which', return_value=True)
@patch('subprocess.Popen')
def test_run_command_success(mock_popen, mock_which):
    """Test run_command with a successful command."""
    mock_process = MagicMock()
    mock_process.communicate.return_value = ('output', 'error')
    mock_popen.return_value = mock_process

    stdout, stderr = run_command(['echo', 'hello'])
    assert stdout == 'output'
    assert stderr == 'error'
    mock_which.assert_called_once_with('echo')
    mock_popen.assert_called_once_with(['echo', 'hello'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       universal_newlines=True)


@patch('shutil.which', return_value=False)
def test_run_command_not_found(mock_which):
    """Test run_command with a nonexistent command."""
    stdout, stderr = run_command(['nonexistent_command'])
    assert stdout == ''
    assert stderr == 'Command not found: nonexistent_command'
    mock_which.assert_called_once_with('nonexistent_command')


@patch('shutil.which', return_value=True)
@patch('subprocess.Popen', side_effect=Exception('Test exception'))
def test_run_command_exception(mock_popen, mock_which):
    """Test run_command with a command that raises an exception"""
    stdout, stderr = run_command(['echo', 'hello'])
    assert stdout == ''
    assert stderr == 'Test exception'
    mock_which.assert_called_once_with('echo')
    mock_popen.assert_called_once_with(['echo', 'hello'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       universal_newlines=True)
