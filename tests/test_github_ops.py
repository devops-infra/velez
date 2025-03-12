from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, call

import pytest
from velez.github_ops import GitHubOperations
from velez.velez import Velez


@pytest.fixture
def github_ops():
    velez = Velez()
    return GitHubOperations(velez)


@patch('velez.github_ops.run_command')
@patch('github.Github.get_user')
@patch('github.Github.get_organization')
def test_init(mock_get_org, mock_get_user, mock_run_command, github_ops):
    """Test GitHubOperations initialization."""
    mock_run_command.side_effect = [
        ('https://github.com/owner/repo.git', ''),
        ('main', '')
    ]
    mock_get_org.return_value.get_repo.return_value = MagicMock()
    mock_get_user.return_value.get_repo.return_value = MagicMock()

    github_ops.__init__(github_ops.velez)
    assert github_ops.repo_url == 'https://github.com/owner/repo.git'
    assert github_ops.repo_name == 'repo'
    assert github_ops.owner_name == 'owner'
    assert github_ops.branch == 'main'


@patch('builtins.input', return_value='')
@patch('velez.github_ops.run_command')
def test_commit(mock_run_command, mock_input, github_ops):
    """Test commit method."""
    github_ops.velez.file_ops = MagicMock()
    github_ops.commit(amend=False)
    mock_run_command.assert_has_calls([
        call(['git', 'add', '-A']),
        call(['git', 'diff', '--compact-summary']),
        call(['git', 'commit'])
    ])


@patch('builtins.input', return_value='')
@patch('velez.github_ops.run_command')
def test_push(mock_run_command, mock_input, github_ops):
    """Test push method."""
    github_ops.push(force=False)
    mock_run_command.assert_has_calls([
        call(['git', 'status']),
        call(['git', 'push', '--set-upstream', 'origin', github_ops.branch])
    ])


@patch('builtins.input', return_value='')
@patch('velez.github_ops.run_command')
def test_push_force(mock_run_command, mock_input, github_ops):
    """Test force push method."""
    github_ops.push(force=True)
    mock_run_command.assert_has_calls([
        call(['git', 'status']),
        call(['git', 'push', '--set-upstream', 'origin', github_ops.branch, '--force'])
    ])


@patch('velez.github_ops.run_command')
def test_create_local_branch(mock_run_command, github_ops):
    """Test create_local_branch method."""
    with patch('builtins.input', return_value='new_branch'):
        github_ops.create_local_branch()
    mock_run_command.assert_called_once_with(['git', 'checkout', '-b', 'new_branch'])


# @patch('velez.github_ops.run_command')
# def test_select_local_branch(mock_run_command, github_ops):
#     """Test select_local_branch method."""
#     mock_run_command.side_effect = [
#         ('', ''),
#         ('* main\n  dev\n', '')
#     ]
#     with patch('pick.pick', return_value=('dev', 1)):
#         github_ops.select_local_branch()
#     mock_run_command.assert_called_with(['git', 'checkout', 'dev'])


# @patch('builtins.input', return_value='')
# @patch('velez.github_ops.run_command')
# @patch('velez.github_ops.pick', return_value=('dev', 1))
# def test_select_remote_branch(mock_pick, mock_run_command, mock_input, github_ops):
#     """Test select_remote_branch method."""
#     mock_run_command.side_effect = [
#         ('', ''),  # First call
#         ('origin/main\norigin/dev\n', ''),  # Second call
#         ('', '')  # Third call (if needed)
#     ]
#     github_ops.select_remote_branch()
#     mock_run_command.assert_has_calls([
#         call(['git', 'checkout', 'origin/dev']),
#         call(['git', 'pull'])
#     ])


# @patch('velez.github_ops.run_command')
# @patch('velez.github_ops.pick', return_value=('dev', 1))
# def test_delete_remote_branch(mock_pick, mock_run_command, github_ops):
#     """Test delete_remote_branch method."""
#     mock_run_command.side_effect = [
#         ('', ''),  # First call
#         ('origin/main\norigin/dev\n', ''),  # Second call
#         ('', '')  # Third call (if needed)
#     ]
#     github_ops.delete_remote_branch()
#     mock_run_command.assert_called_with(['git', 'push', 'origin', '--delete', 'dev'])


# @patch('builtins.input', side_effect=['PR Title', 'PR Description', ''])
# @patch('velez.github_ops.run_command')
# @patch('github.Repository.Repository.create_pull')
# def test_create_pull_request(mock_create_pull, mock_run_command, github_ops):
#     """Test create_pull_request method."""
#     mock_run_command.side_effect = [
#         ('main', ''),  # Current branch
#         ('feature-branch', '')  # Head branch
#     ]
#     github_ops.create_pull_request()
#     mock_create_pull.assert_called_once_with(
#         title='PR Title',
#         body='PR Description',
#         head='feature-branch',
#         base='main'
#     )


# @patch('builtins.input', side_effect=['Issue Title', 'Issue Description', ''])
# @patch('velez.github_ops.run_command')
# @patch('github.Repository.Repository.create_issue')
# def test_create_issue(mock_create_issue, mock_run_command, github_ops):
#     """Test create_issue method."""
#     mock_run_command.return_value = ('', '')  # Simulate successful command execution
#     github_ops.create_issue()
#     mock_create_issue.assert_called_once_with(
#         title='Issue Title',
#         body='Issue Description'
#     )


@patch('velez.github_ops.run_command')
@patch('github.Repository.Repository.get_pulls')
def test_list_open_pull_requests(mock_get_pulls, mock_run_command, github_ops):
    """Test list_open_pull_requests method."""
    mock_get_pulls.return_value = [
        MagicMock(number=1, title='PR 1', html_url='http://example.com/pr1'),
        MagicMock(number=2, title='PR 2', html_url='http://example.com/pr2')
    ]
    with patch('builtins.input', return_value=''):
        github_ops.list_open_pull_requests(repo_only=True)
    mock_get_pulls.assert_called_once_with(state='open')


@patch('velez.github_ops.run_command')
@patch('github.Repository.Repository.get_issues')
def test_list_open_issues(mock_get_issues, mock_run_command, github_ops):
    """Test list_open_issues method."""
    mock_get_issues.return_value = [
        MagicMock(number=1, title='Issue 1', html_url='http://example.com/issue1'),
        MagicMock(number=2, title='Issue 2', html_url='http://example.com/issue2')
    ]
    with patch('builtins.input', return_value=''):
        github_ops.list_open_issues(repo_only=True)
    mock_get_issues.assert_called_once_with(state='open')


# @patch('velez.github_ops.run_command')
# @patch('github.Repository.Repository.get_branches')
# @patch('github.Repository.Repository.get_branch')
# @patch('github.Repository.Repository.compare')
# def test_get_stale_branches(mock_compare, mock_get_branch, mock_get_branches, mock_run_command, github_ops):
#     """Test get_stale_branches method."""
#     mock_get_branches.return_value = [
#         MagicMock(name='main', commit=MagicMock(sha='sha-main')),
#         MagicMock(name='feature', commit=MagicMock(sha='sha-feature'))
#     ]
#     mock_get_branch.return_value = MagicMock(commit=MagicMock(sha='sha-main'))
#     mock_compare.return_value.behind_by = 31  # Set commits_behind
#     mock_compare.return_value.ahead_by = 0  # Set ahead_by
#     mock_get_branch.return_value.commit.commit.author.date = datetime.now() - timedelta(
#         days=32)  # Set days_since_last_commit
#     stale_branches = github_ops.get_stale_branches()
#     assert stale_branches == ['feature']
