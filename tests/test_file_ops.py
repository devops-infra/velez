import pytest
from unittest.mock import patch, MagicMock, mock_open
from velez.file_ops import FileOperations
from velez.velez import Velez

@pytest.fixture
def file_ops():
    velez = Velez()
    return FileOperations(velez)

@patch('velez.file_ops.run_command')
def test_format_hcl_files_tf(mock_run_command, file_ops):
    """Test format_hcl_files with Terraform."""
    file_ops.velez.check_terragrunt = MagicMock(return_value=True)
    file_ops.velez.get_tf_ot = MagicMock(return_value='terraform')
    file_ops.format_hcl_files()
    mock_run_command.assert_any_call(['terragrunt', 'hclfmt'])
    mock_run_command.assert_any_call(['terraform', 'fmt', '-recursive', '.'])

@patch('velez.file_ops.run_command')
def test_format_hcl_files_ot(mock_run_command, file_ops):
    """Test format_hcl_files with OpenTofu."""
    file_ops.velez.check_terragrunt = MagicMock(return_value=True)
    file_ops.velez.get_tf_ot = MagicMock(return_value='tofu')
    file_ops.format_hcl_files()
    mock_run_command.assert_any_call(['terragrunt', 'hclfmt'])
    mock_run_command.assert_any_call(['tofu', 'fmt', '-recursive', '.'])

@patch('builtins.input', return_value='')  # Mock input to return an empty string
@patch('os.remove')
@patch('shutil.rmtree')
def test_clean_files(mock_rmtree, mock_remove, mock_input, file_ops):
    """Test clean_files."""
    with patch('os.walk') as mock_walk:
        mock_walk.return_value = [
            ('/path', ['.terraform'], ['.terraform.lock.hcl', 'tfplan']),
            ('/path/.terraform', [], []),
        ]
        file_ops.clean_files('/path')
        mock_rmtree.assert_any_call('/path/.terraform')
        mock_remove.assert_any_call('/path/.terraform.lock.hcl')
        mock_remove.assert_any_call('/path/tfplan')

@patch('builtins.open', new_callable=mock_open, read_data='key = "value"')
@patch('velez.file_ops.hcl2.load', return_value={"key": "value"})
def test_load_hcl_file(mock_hcl_load, mock_file):
    """Test load_hcl_file."""
    result = FileOperations.load_hcl_file('dummy.hcl')
    assert result == {"key": "value"}
    mock_file.assert_called_once_with('dummy.hcl', 'r')
    mock_hcl_load.assert_called_once()

@patch('builtins.open', new_callable=mock_open, read_data='{"key": "value"}')
def test_load_json_file(mock_file):
    """Test load_json_file."""
    result = FileOperations.load_json_file('dummy.json')
    assert result == {"key": "value"}
    mock_file.assert_called_once_with('dummy.json', 'r')
