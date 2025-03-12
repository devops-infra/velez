import os
import re
import sys
from datetime import datetime

import github
from pick import pick
from velez.file_ops import FileOperations
from velez.utils import STR_BACK, STR_EXIT, run_command

STALE_BRANCHES_DAYS = int(os.getenv('GITHUB_STALE_BRANCHES_DAYS', 45))
STALE_BRANCHES_COMMITS = int(os.getenv('GITHUB_STALE_BRANCHES_COMMITS', 30))

STR_COMMIT = "→ Commit"
STR_AMEND = "⇢ Amend commit"
STR_PUSH = "⇧ Push"
STR_PUSH_FORCE = "⇪ Force push"
STR_UPDATE = "↓ Pull menu"
STR_BRANCHES = "⌥ Branches menu"
STR_PULL_REQUESTS = "⌲ Pull Requests menu"
STR_ISSUES = "⌳ Issues menu"
STR_REBASE = "⇲ Rebase"
STR_PULL = "↘︎ Pull"
STR_NEW_BRANCH = "✦ Create new branch"
STR_SELECT_LOCAL_BRANCH = "☞ Select local branch"
STR_SELECT_REMOTE_BRANCH = "☛ Select remote branch"
STR_DELETE_LOCAL_BRANCH = "⌫ Delete local branch"
STR_DELETE_REMOTE_BRANCH = "⌦ Delete remote branch"
STR_CREATE_PR = "✯ Create pull request"
STR_LIST_PR_REPO = "⎗ List PRs in the repository"
STR_LIST_PR_ORG = "⎘ List PRs for the whole organization"
STR_CREATE_ISSUE = "✶ Create new issue"
STR_LIST_ISSUES_REPO = "⎗ List issues in the repository"
STR_LIST_ISSUES_ORG = "⎘ List issues for the whole organization"
STR_DELETE_STALE_BRANCHES = "⌦ Delete stale branches"


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
            STR_COMMIT,
            STR_AMEND,
            STR_PUSH,
            STR_PUSH_FORCE,
            STR_UPDATE,
            STR_BRANCHES,
            STR_PULL_REQUESTS,
            STR_ISSUES,
            STR_BACK,
            STR_EXIT
        ]
        option, index = pick(options, title)

        if option == STR_COMMIT:
            self.commit(amend=False)
        elif option == STR_AMEND:
            self.commit(amend=True)
        elif option == STR_PUSH:
            self.push(force=False)
        elif option == STR_PUSH_FORCE:
            self.push(force=True)
        elif option == STR_UPDATE:
            self.update_menu()
        elif option == STR_BRANCHES:
            self.branches_menu()
        elif option == STR_PULL_REQUESTS:
            self.pull_request_menu()
        elif option == STR_ISSUES:
            self.issues_menu()
        elif option == STR_BACK:
            self.velez.main_menu()
        elif option == STR_EXIT:
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

        # format HCL files before committing
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
            STR_REBASE,
            STR_PULL,
            STR_BACK,
            STR_EXIT
        ]
        option, index = pick(options, title)

        if option == STR_REBASE:
            run_command(['git', 'pull', '--rebase'])
        elif option == STR_PULL:
            run_command(['git', 'pull'])
        elif option == STR_BACK:
            self.github_menu()
        elif option == STR_EXIT:
            sys.exit()

        self.update_menu()

    def branches_menu(self) -> None:
        """
        Display branches submenu.
        :return: None
        """
        title = f"Current branch: {self.branch}. Choose a branch operation:"
        options = [
            STR_NEW_BRANCH,
            STR_SELECT_LOCAL_BRANCH,
            STR_SELECT_REMOTE_BRANCH,
            STR_DELETE_LOCAL_BRANCH,
            STR_DELETE_REMOTE_BRANCH,
            STR_DELETE_STALE_BRANCHES,
            STR_BACK,
            STR_EXIT
        ]
        option, index = pick(options, title)

        if option == STR_NEW_BRANCH:
            self.create_local_branch()
        elif option == STR_SELECT_LOCAL_BRANCH:
            self.select_local_branch()
        elif option == STR_SELECT_REMOTE_BRANCH:
            self.select_remote_branch()
        elif option == STR_DELETE_LOCAL_BRANCH:
            self.delete_local_branch()
        elif option == STR_DELETE_REMOTE_BRANCH:
            self.delete_remote_branch()
        elif option == STR_DELETE_STALE_BRANCHES:
            self.delete_stale_branches()
        elif option == STR_BACK:
            self.github_menu()
        elif option == STR_EXIT:
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
        branches += [STR_BACK, STR_EXIT]
        title = f"Current branch: {self.branch}. Select a local branch:"
        option, index = pick(branches, title)
        if option == STR_BACK:
            self.branches_menu()
        elif option == STR_EXIT:
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
        branches += [STR_BACK, STR_EXIT]
        title = f"Current branch: {self.branch}. Select a remote branch:"
        option, index = pick(branches, title)
        if option == STR_BACK:
            self.branches_menu()
        elif option == STR_EXIT:
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
        branches += [STR_BACK, STR_EXIT]
        title = f"Current branch: {self.branch}. Select a local branch to delete:"
        option, index = pick(branches, title)
        if option == STR_BACK:
            self.branches_menu()
        elif option == STR_EXIT:
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
        branches += [STR_BACK, STR_EXIT]
        title = f"Current branch: {self.branch}. Select a remote branch to delete:"
        option, index = pick(branches, title)
        if option == STR_BACK:
            self.branches_menu()
        elif option == STR_EXIT:
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
            STR_CREATE_PR,
            STR_LIST_PR_REPO,
            STR_LIST_PR_ORG,
            STR_BACK,
            STR_EXIT
        ]
        option, index = pick(options, title)

        if option == STR_CREATE_PR:
            self.create_pull_request()
        elif option == STR_LIST_PR_REPO:
            self.list_open_pull_requests(repo_only=True)
        elif option == STR_LIST_PR_ORG:
            self.list_open_pull_requests(repo_only=False)
        elif option == STR_BACK:
            self.github_menu()
        elif option == STR_EXIT:
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
            STR_CREATE_ISSUE,
            STR_LIST_ISSUES_REPO,
            STR_LIST_ISSUES_ORG,
            STR_BACK,
            STR_EXIT
        ]
        option, index = pick(options, title)

        if option == STR_CREATE_ISSUE:
            self.create_issue()
        elif option == STR_LIST_ISSUES_REPO:
            self.list_open_issues(repo_only=True)
        elif option == STR_LIST_ISSUES_ORG:
            self.list_open_issues(repo_only=False)
        elif option == STR_BACK:
            self.github_menu()
        elif option == STR_EXIT:
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

    def get_stale_branches(self) -> list:
        """
        Get a list of stale branches based on the set criteria.
        :return: list of stale branches
        """
        stale_branches = []
        branches = self.repo.get_branches()
        main_branch = self.repo.get_branch(self.repo.default_branch)
        main_branch_commit = main_branch.commit

        for branch in branches:
            if branch.name == main_branch.name:
                continue

            branch_commit = branch.commit
            commit_date = branch_commit.commit.author.date
            days_since_last_commit = (datetime.now(tz=commit_date.tzinfo) - commit_date).days
            commits_behind = self.repo.compare(main_branch_commit.sha, branch_commit.sha).behind_by

            if days_since_last_commit > STALE_BRANCHES_DAYS or commits_behind > STALE_BRANCHES_COMMITS:
                stale_branches.append(branch.name)

        return stale_branches

    def delete_stale_branches(self) -> None:
        """
        Delete stale branches based on the set criteria.
        :return: None
        """
        stale_branches = self.get_stale_branches()
        if not stale_branches:
            print("No stale branches found.")
            input("Press Enter to return to the branches menu...")
            return

        title = f"Current branch: {self.branch}. Select a stale branch to delete:"
        option, index = pick(stale_branches + [STR_BACK, STR_EXIT], title)
        if option == STR_BACK:
            self.branches_menu()
        elif option == STR_EXIT:
            sys.exit()
        else:
            run_command(['git', 'push', 'origin', '--delete', option])
            input("Press Enter to return to the branches menu...")
