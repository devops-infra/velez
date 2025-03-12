from unittest.mock import patch

import pytest
from velez.terragrunt_ops import TerragruntOperations
from velez.velez import Velez


@pytest.fixture
def terragrunt_ops():
    velez = Velez()
    return TerragruntOperations(velez)

@patch('velez.terragrunt_ops.run_command')
def test_get_terraform_version(mock_run_command, terragrunt_ops):
    """Test get_terraform_version method."""
    mock_run_command.return_value = ('Terraform v1.0.0', '')
    version = terragrunt_ops.get_terraform_version()
    assert version == '1.0.0'
    mock_run_command.assert_called_once_with(['terraform', '-version'], quiet=True)


@patch('velez.terragrunt_ops.run_command')
def test_get_opentofu_version(mock_run_command, terragrunt_ops):
    """Test get_opentofu_version method."""
    mock_run_command.return_value = ('OpenTofu v1.0.0', '')
    version = terragrunt_ops.get_opentofu_version()
    assert version == '1.0.0'
    mock_run_command.assert_called_once_with(['tofu', '--version'], quiet=True)


@patch('velez.terragrunt_ops.run_command')
def test_get_terragrunt_version(mock_run_command, terragrunt_ops):
    """Test get_terragrunt_version method."""
    mock_run_command.return_value = ('terragrunt version v0.35.0', '')
    version = terragrunt_ops.get_terragrunt_version()
    assert version == '0.35.0'
    mock_run_command.assert_called_once_with(['terragrunt', '--version'], quiet=True)


@patch('velez.terragrunt_ops.run_command')
def test_plan_action(mock_run_command, terragrunt_ops):
    """Test plan_action method."""
    terragrunt_ops.plan_action()
    mock_run_command.assert_called_once_with(['plan'])


@patch('velez.terragrunt_ops.run_command')
def test_apply_action(mock_run_command, terragrunt_ops):
    """Test apply_action method."""
    terragrunt_ops.apply_action()
    mock_run_command.assert_called_once_with(['apply'])


@patch('velez.terragrunt_ops.run_command')
def test_destroy_action(mock_run_command, terragrunt_ops):
    """Test destroy_action method."""
    terragrunt_ops.destroy_action()
    mock_run_command.assert_called_once_with(['destroy'])


@patch('velez.terragrunt_ops.run_command')
def test_output_action(mock_run_command, terragrunt_ops):
    """Test output_action method."""
    terragrunt_ops.output_action()
    mock_run_command.assert_called_once_with(['output'])


@patch('velez.terragrunt_ops.run_command')
def test_init_action(mock_run_command, terragrunt_ops):
    """Test init_action method."""
    terragrunt_ops.init_action()
    mock_run_command.assert_called_once_with(['init'])


@patch('velez.terragrunt_ops.run_command')
def test_validate_action(mock_run_command, terragrunt_ops):
    """Test validate_action method."""
    terragrunt_ops.validate_action()
    mock_run_command.assert_called_once_with(['validate'])


@patch('velez.terragrunt_ops.run_command')
def test_refresh_action(mock_run_command, terragrunt_ops):
    """Test refresh_action method."""
    terragrunt_ops.refresh_action()
    mock_run_command.assert_called_once_with(['refresh'])


@patch('velez.terragrunt_ops.run_command')
@patch('velez.terragrunt_ops.FileOperations.load_json_file', return_value={})
def test_load_terragrunt_config(mock_load_json_file, mock_run_command, terragrunt_ops):
    """Test load_terragrunt_config method."""
    config = terragrunt_ops.load_terragrunt_config()
    assert config == {}
    mock_run_command.assert_called_once_with(['terragrunt', 'render-json', '--out', terragrunt_ops.temp_config],
                                             quiet=True)
    mock_load_json_file.assert_called_once_with(terragrunt_ops.temp_config)


@patch('velez.terragrunt_ops.run_command')
def test_run_terragrunt(mock_run_command, terragrunt_ops):
    """Test run_terragrunt method."""
    terragrunt_ops.run_terragrunt(['plan'])
    mock_run_command.assert_called_once_with(['terragrunt', 'plan'], quiet=False)
