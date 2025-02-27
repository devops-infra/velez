import os
import re
import sys

import github
from pick import pick
from velez.file_ops import FileOperations
from velez.utils import str_back, str_exit, run_command

str_commit = "→ Commit"
str_amend = "⇢ Amend commit"
str_push = "⇧ Push"
str_push_force = "⇪ Force push"
str_update = "↓ Pull menu"
str_branches = "⌥ Branches menu"
str_pull_requests = "⌲ Pull Requests menu"
str_issues = "⌳ Issues menu"
str_rebase = "⇲ Rebase"
str_pull = "↘︎ Pull"
str_new_branch = "✦ Create new branch"
str_select_local_branch = "☞ Select local branch"
str_select_remote_branch = "☛ Select remote branch"
str_delete_local_branch = "⌫ Delete local branch"
str_delete_remote_branch = "⌦ Delete remote branch"
str_create_pr = "✯ Create pull request"
str_list_pr_repo = "⎗ List PRs in the repository"
str_list_pr_org = "⎘ List PRs for the whole organization"
str_create_issue = "✶ Create new issue"
str_list_issues_repo = "⎗ List issues in the repository"
str_list_issues_org = "⎘ List issues for the whole organization"


class GitHubOperations:
    """
    Class for GitHub operations.
    """

    def __init__(self, velez):
        self.velez = velez
        if not self.velez.check_github():
            input("Press Enter to return to the main menu...")
            self.velez.main_menu()
        auth = github.Auth.Token(os.getenv('GITHUB_TOKEN'))
        with github.Github(auth=auth) as gh:
            self.gh = gh
            self.repo_url = run_command(['git', 'remote', 'get-url', 'origin'], quiet=True)[0].strip()
            self.repo_name = self.repo_url.split('/')[-1].replace('.git', '')
            self.owner_name = self.repo_url.split('/')[-2]
            self.full_name = f"{self.owner_name}/{self.repo_name}"
            self.branch = run_command(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], quiet=True)[0].strip()
            try:
                org = self.gh.get_organization(self.owner_name)
            except github.GithubException:
                org = None
            if org:
                self.repo = org.get_repo(self.repo_name)
            else:
                self.repo = self.gh.get_user(self.owner_name).get_repo(self.repo_name)

    def github_menu(self) -> None:
        """
        Display GitHub operations menu.
        :return: None
        """
        title = f"Current branch: {self.branch}. Choose a GitHub operation:"
        options = [
            str_commit,
            str_amend,
            str_push,
            str_push_force,
            str_update,
            str_branches,
            str_pull_requests,
            str_issues,
            str_back,
            str_exit
        ]
        option, index = pick(options, title)

        if option == str_commit:
            self.commit(amend=False)
        elif option == str_amend:
            self.commit(amend=True)
        elif option == str_push:
            self.push(force=False)
        elif option == str_push_force:
            self.push(force=True)
        elif option == str_update:
            self.update_menu()
        elif option == str_branches:
            self.branches_menu()
        elif option == str_pull_requests:
            self.pull_request_menu()
        elif option == str_issues:
            self.issues_menu()
        elif option == str_back:
            self.velez.main_menu()
        elif option == str_exit:
            sys.exit()

        self.github_menu()

    def commit(self, amend: bool = False) -> None:
        """
        Add all files to the staging area and commit them.
        Can also amend the last commit.
        :param amend: if True, amend the last commit
        :return: None
        """
        run_command(['git', 'add', '-A'])

        # format HCL files before commiting
        if self.velez.file_ops is None:
            self.velez.file_ops = FileOperations(self.velez)
        self.velez.file_ops.format_hcl_files()

        run_command(['git', 'diff', '--compact-summary'])
        git_command = ['git', 'commit']
        if amend:
            git_command.append('--amend')
        run_command(git_command)
        input("Press Enter to return to the GitHub menu...")

    def push(self, force: bool = False) -> None:
        """
        Push commits to the currently selected branch.
        Can also force push.
        :param force: if True, force push
        :return: None
        """
        run_command(['git', 'status'])
        if force:
            run_command(['git', 'push', '--set-upstream', 'origin', self.branch, '--force'])
        else:
            run_command(['git', 'push', '--set-upstream', 'origin', self.branch])
        input("Press Enter to return to the GitHub menu...")

    def update_menu(self) -> None:
        """
        Display update submenu.
        :return: None
        """
        title = f"Current branch: {self.branch}. Choose an update operation:"
        options = [
            str_rebase,
            str_pull,
            str_back,
            str_exit
        ]
        option, index = pick(options, title)

        if option == str_rebase:
            run_command(['git', 'pull', '--rebase'])
        elif option == str_pull:
            run_command(['git', 'pull'])
        elif option == str_back:
            self.github_menu()
        elif option == str_exit:
            sys.exit()

        self.update_menu()

    def branches_menu(self) -> None:
        """
        Display branches submenu.
        :return: None
        """
        title = f"Current branch: {self.branch}. Choose a branch operation:"
        options = [
            str_new_branch,
            str_select_local_branch,
            str_select_remote_branch,
            str_delete_local_branch,
            str_delete_remote_branch,
            str_back,
            str_exit
        ]
        option, index = pick(options, title)

        if option == str_new_branch:
            self.create_local_branch()
        elif option == str_select_local_branch:
            self.select_local_branch()
        elif option == str_select_remote_branch:
            self.select_remote_branch()
        elif option == str_delete_local_branch:
            self.delete_local_branch()
        elif option == str_delete_remote_branch:
            self.delete_remote_branch()
        elif option == str_back:
            self.github_menu()
        elif option == str_exit:
            sys.exit()

        self.branches_menu()

    def create_local_branch(self) -> None:
        """
        Create a new local branch.
        :return: None
        """
        self.branch = input("Enter new branch name: ")
        run_command(['git', 'checkout', '-b', self.branch])
        input("Press Enter to return to the branches menu...")

    def select_local_branch(self) -> None:
        """
        Select a local branch.
        :return: None
        """
        run_command(['git', 'fetch', '--all'])
        branches = run_command(['git', 'branch', '--all'])[0].split('\n')
        branches = [re.sub(r'^\* ', '', branch.strip()) for branch in branches if branch]
        branches += [str_back, str_exit]
        title = f"Current branch: {self.branch}. Select a local branch:"
        option, index = pick(branches, title)
        if option == str_back:
            self.branches_menu()
        elif option == str_exit:
            sys.exit()
        else:
            self.branch = option
            run_command(['git', 'checkout', option])
        input("Press Enter to return to the branches menu...")

    def select_remote_branch(self) -> None:
        """
        Select a remote branch.
        :return: None
        """
        run_command(['git', 'fetch', '--all'])
        branches = run_command(['git', 'branch', '--remote'])[0].split('\n')
        branches = [branch.strip() for branch in branches if branch]
        branches += [str_back, str_exit]
        title = f"Current branch: {self.branch}. Select a remote branch:"
        option, index = pick(branches, title)
        if option == str_back:
            self.branches_menu()
        elif option == str_exit:
            sys.exit()
        else:
            run_command(['git', 'checkout', option])
            run_command(['git', 'pull'])
        input("Press Enter to return to the branches menu...")

    def delete_local_branch(self) -> None:
        """
        Delete a local branch.
        :return: None
        """
        run_command(['git', 'fetch', '--prune'])
        branches = run_command(['git', 'branch'])[0].split('\n')
        branches = [branch.strip() for branch in branches if branch]
        branches += [str_back, str_exit]
        title = f"Current branch: {self.branch}. Select a local branch to delete:"
        option, index = pick(branches, title)
        if option == str_back:
            self.branches_menu()
        elif option == str_exit:
            sys.exit()
        else:
            run_command(['git', 'branch', '--delete', option])
        input("Press Enter to return to the branches menu...")

    def delete_remote_branch(self) -> None:
        """
        Delete a remote branch.
        :return: None
        """
        run_command(['git', 'fetch', '--prune'])
        branches = run_command(['git', 'branch', '--remote'])[0].split('\n')
        branches = [re.sub(r'^origin/', '', branch.strip()) for branch in branches if branch]
        branches += [str_back, str_exit]
        title = f"Current branch: {self.branch}. Select a remote branch to delete:"
        option, index = pick(branches, title)
        if option == str_back:
            self.branches_menu()
        elif option == str_exit:
            sys.exit()
        else:
            run_command(['git', 'push', 'origin', '--delete', option])
        input("Press Enter to return to the branches menu...")

    def pull_request_menu(self) -> None:
        """
        Display pull request submenu.
        :return: None
        """
        title = "Choose a pull request operation:"
        options = [
            str_create_pr,
            str_list_pr_repo,
            str_list_pr_org,
            str_back,
            str_exit
        ]
        option, index = pick(options, title)

        if option == str_create_pr:
            self.create_pull_request()
        elif option == str_list_pr_repo:
            self.list_open_pull_requests(repo_only=True)
        elif option == str_list_pr_org:
            self.list_open_pull_requests(repo_only=False)
        elif option == str_back:
            self.github_menu()
        elif option == str_exit:
            sys.exit()

        self.pull_request_menu()

    def create_pull_request(self) -> None:
        """
        Create a pull request from the current branch.
        :return: None
        """
        base_branch = self.repo.default_branch
        head_branch = run_command(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], quiet=True)[0].strip()
        title = input("Enter the pull request title: ")
        body = input("Enter the pull request description: ")

        pr = self.repo.create_pull(title=title, body=body, head=head_branch, base=base_branch)
        print(f"Pull request created: {pr.html_url}")
        input("Press Enter to return to the GitHub menu...")

    def list_open_pull_requests(self, repo_only: bool) -> None:
        """
        List open pull requests in the repository or the whole organization.
        :param repo_only: if True, list pull requests for the repository only
        :return: None
        """
        if repo_only:
            pull_requests = self.repo.get_pulls(state='open')
        else:
            org = self.gh.get_organization(self.owner_name)
            pull_requests = []
            for repo in org.get_repos():
                pull_requests.extend(repo.get_pulls(state='open'))

        for pr in pull_requests:
            print(f"#{pr.number} - {pr.title}\nURL: {pr.html_url}\n")
        input("Press Enter to return to the GitHub menu...")

    def issues_menu(self) -> None:
        """
        Display issues submenu.
        :return: None
        """
        title = "Choose an issue operation:"
        options = [
            str_create_issue,
            str_list_issues_repo,
            str_list_issues_org,
            str_back,
            str_exit
        ]
        option, index = pick(options, title)

        if option == str_create_issue:
            self.create_issue()
        elif option == str_list_issues_repo:
            self.list_open_issues(repo_only=True)
        elif option == str_list_issues_org:
            self.list_open_issues(repo_only=False)
        elif option == str_back:
            self.github_menu()
        elif option == str_exit:
            sys.exit()

        self.issues_menu()

    def create_issue(self) -> None:
        """
        Create a new issue.
        :return: None
        """
        title = input("Enter the issue title: ")
        body = input("Enter the issue description: ")

        issue = self.repo.create_issue(title=title, body=body)
        print(f"Issue created: {issue.html_url}")
        input("Press Enter to return to the GitHub menu...")

    def list_open_issues(self, repo_only: bool) -> None:
        """
        List open issues in the repository or the whole organization.
        :param repo_only: if True, list issues for the repository only
        :return: None
        """
        if repo_only:
            issues = self.repo.get_issues(state='open')
        else:
            org = self.gh.get_organization(self.owner_name)
            issues = []
            for repo in org.get_repos():
                issues.extend(repo.get_issues(state='open'))

        for issue in issues:
            print(f"#{issue.number} - {issue.title}\nURL: {issue.html_url}\n")
        input("Press Enter to return to the GitHub menu...")
