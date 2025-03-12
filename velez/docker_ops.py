import datetime
import json
import os
import sys

import requests
from pick import pick
from requests import Response
from velez.utils import STR_BACK, STR_EXIT, get_date_str, print_markdown_table, get_datetime, bytes_to_human_readable

STR_MANAGE_REPOSITORIES = "️📱 Manage repositories"
STR_REMOVE_IMAGES_NOT_PULLED_IN_X_DAYS = "📆 Remove images not pulled in X days"
STR_LIST_LAST_TAGS = "🆕 List last tags"
STR_DELETE_STALE_TAGS = "😐 Delete stale tags"
STR_DELETE_UNTAGGED_IMAGES = "🔖 Delete untagged images"
STR_DELETE_TAGS_WITH_PREFIX = "🛫 Delete tags with defined prefix"
STR_DELETE_TAGS_WITH_SUFFIX = "🛬 Delete tags with defined suffix"
STR_DELETE_TAG = "🗑️ Delete specific tag"
STR_MANAGE_ORGANIZATION = "💠 Manage organization"
STR_MANAGE_USERS = "👤 Manage users"
STR_MANAGE_TEAMS_GROUPS = "👥 Manage teams/groups"
STR_GROUP_MEMBERSHIP = "👥 Group membership"
STR_LIST_MEMBERS = "👤 List members"
STR_INVITE_USER = "➕ Invite user to organization"
STR_UPDATE_MEMBER_ROLE = "🔄 Update member role"
STR_REMOVE_MEMBER = "➖ Remove member from organization"
STR_LIST_GROUPS = "👥 List groups"
STR_CREATE_GROUP = "➕ Create group"
STR_UPDATE_GROUP_DETAILS = "🔄 Update group details"
STR_DELETE_GROUP = "➖ Delete group"
STR_LIST_GROUP_MEMBERS = "👤 List group members"
STR_ADD_MEMBER_TO_GROUP = "➕ Add member to group"
STR_REMOVE_MEMBER_FROM_GROUP = "➖ Remove member from group"
STR_MANAGE_PERSONAL = "👦 Manage personal repositories"
STR_SAVE_TAGS_FILE = "💾 Save tags to file"
DOCKER_HUB_API = "https://hub.docker.com/v2"


def get_username(quiet: bool = True) -> str:
    """
    Get the username from the environment variable or prompt the user.
    :param quiet: Quiet mode
    :return: Username as a string
    """
    username = os.getenv("DOCKER_USERNAME", None)
    if not username and not quiet:
        username = input("Enter your Docker Hub username (env var preferred): ")
    return username


def get_token(quiet: bool = True) -> str:
    """
    Get the token from the environment variable or prompt the user.
    :param quiet: Quiet mode
    :return: PAT or OAT as a string
    """
    token = os.getenv("DOCKER_TOKEN", None)
    if not token and not quiet:
        token = input("Enter your Docker Hub token (env var preferred): ")
    return token


def get_repository(quiet: bool = True) -> str:
    """
    Get the repository name from the environment variable or prompt the user for it.
    :param quiet: Quiet mode
    :return: Repository name as a string
    """
    repository = os.getenv("DOCKER_REPOSITORY", None)
    if not repository:
        folder = os.path.basename(os.getcwd())
        if quiet:
            repository = folder
        else:
            prompt = f"Enter the repository name (default: {folder}): "
            repository = input(prompt)
            if repository == '':
                repository = folder
    return repository


def get_ownership(quiet: bool = True) -> tuple[str, bool]:
    """
    Get the owner from the environment variable DOCKER_OWNER and:
    - check if it is a valid Docker organization.
    - check if parent folder name is a valid Docker organization.
    - if not, ask user for the owner name.
    :param quiet: Quiet mode
    :return: Owner name and a boolean indicating if it is an organization
    """
    owner = os.getenv("DOCKER_OWNER", None)
    if owner:
        if check_organization(owner):
            return owner, True
        return owner, False
    # guess the owner name from the parent folder name; docker organizations don't have '-' in their names
    parent_folder = os.path.basename(os.path.dirname(os.getcwd())).replace('-', '')
    if quiet:
        return parent_folder, check_organization(parent_folder)
    prompt = f"Enter the owner name (default: {parent_folder}): "
    owner = input(prompt)
    if owner == '':
        owner = parent_folder
    return owner, check_organization(owner)


def call_api(method: str, url: str, params: str = None, payload: dict = None, auth: tuple = None,
             headers: dict = None) -> Response:
    """
    Call the Docker Hub API.
    :param method: HTTP method (GET, POST, DELETE, etc.)
    :param url: last part URL, after the API endpoint .../v2/...
    :param params: Query parameters for the request
    :param payload: JSON payload for the request
    :param auth: Authentication tuple (username, token)
    :param headers: Headers for the request
    :return: Response object from the request
    """
    try:
        response = requests.request(method, f"{DOCKER_HUB_API}/{url}", params=params, timeout=10,
                                    headers=headers, auth=auth, json=payload)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error doing {method} on {url}: {e}")
        print(f"Response {e.response.status_code}: {e.response.json()}")
        input("Press Enter to return to the previous menu...")
        return e.response


def check_organization(name: str) -> bool:
    """
    Check if the given name is a Docker organization .
    :param name: Organization name
    :return: True if valid, False otherwise
    """
    response = call_api("GET", f"orgs/{name}")
    if response.status_code == 200:
        return True
    return False


def get_bearer_token(identity: str, token: str) -> str:
    """
    Obtain a fresh token from Docker Hub.
    :param identity: Docker Hub username or organization name
    :param token: Docker Hub PAT or OAT
    :return: Token as a string
    """
    payload = {
        "identifier": identity,
        "secret": token
    }
    response = call_api("POST", "auth/token", payload=payload)
    return response.json().get("access_token")


class DockerOperations:
    """
    Class for Docker operations.
    Using: https://docs.docker.com/reference/api/hub/latest/
    """

    def __init__(self, velez):
        self.velez = velez
        self.username = get_username()
        self.token = get_token()
        # stop if username or token are not set
        if not self.username or not self.token:
            print("Error: Username and token must be provided.")
            sys.exit(1)
        self.owner, self.organization = get_ownership(quiet=True)
        if self.organization:
            identifier = self.owner
        else:
            identifier = self.username
        self.headers = {
            "Authorization": f"Bearer {get_bearer_token(identifier, self.token)}",
        }
        self.auth = (self.username, self.token)
        self.repository = get_repository(quiet=True)
        self.tags = None  # will be updated when listing tags with selected number of tags

    def verify_organization(self) -> None:
        """
        Check if the owner is a Docker organization.
        :return: None
        """
        if not self.organization:
            print(f"{self.owner} is not a Docker organization.")
            input("Press Enter to return to the Docker menu...")
            self.docker_menu()

    def docker_menu(self) -> None:
        """
        Display Docker operations menu.
        :return: None
        """
        title = "Choose a Docker operation:"
        options = [
            STR_MANAGE_REPOSITORIES,
            STR_MANAGE_ORGANIZATION,
            STR_BACK,
            STR_EXIT
        ]
        option, index = pick(options, title)

        if option == STR_MANAGE_REPOSITORIES:
            self.manage_repositories()
        elif option == STR_MANAGE_ORGANIZATION:
            self.manage_organization()
        elif option == STR_BACK:
            self.velez.main_menu()
        elif option == STR_EXIT:
            sys.exit()

        self.docker_menu()

    def manage_repositories(self) -> None:
        """
        Choose a repository.
        :return: None
        """
        if not self.repository:
            self.repository = get_repository(quiet=False)
        if not self.owner:
            self.owner, self.organization = get_ownership(quiet=False)

        # get repositories for the owner
        response = call_api("GET", f"repositories/{self.owner}", auth=self.auth)
        repositories = response.json()['results']
        # sort repositories by name and add current repository at the top
        repo_names = [repo['name'] for repo in repositories]
        repo_names.sort()
        if self.repository:
            repo_names.insert(0, f"{self.repository} (current)")

        # display the list of repositories
        title = f"Choose a repository for {self.owner}:"
        options = repo_names + [STR_BACK, STR_EXIT]
        option, index = pick(options, title)
        if option == STR_BACK:
            self.docker_menu()
        elif option == STR_EXIT:
            sys.exit()
        else:
            self.repository = option.replace(" (current)", "")
            self.repository_menu()

    def repository_menu(self) -> None:
        """
        Display repository menu.
        :return: None
        """
        title = f"Chose repository action for {self.owner}/{self.repository}:"
        options = [
            STR_LIST_LAST_TAGS,
            STR_SAVE_TAGS_FILE,
            # STR_DELETE_TAG, # TODO: Waiting to be implemented in the API
            # STR_DELETE_STALE_TAGS, # TODO: Waiting to be implemented in the API
            # STR_DELETE_UNTAGGED_IMAGES, # TODO: Waiting to be implemented in the API
            # STR_DELETE_TAGS_WITH_PREFIX, # TODO: Waiting to be implemented in the API
            # STR_DELETE_TAGS_WITH_SUFFIX, # TODO: Waiting to be implemented in the API
            STR_BACK,
            STR_EXIT
        ]
        option, index = pick(options, title)

        if option == STR_LIST_LAST_TAGS:
            self.list_last_tags()
        elif option == STR_SAVE_TAGS_FILE:
            self.save_tags_file()
        elif option == STR_DELETE_TAG:
            tag = input("Enter the tag to delete: ")
            self.delete_tag(tag)
        elif option == STR_DELETE_STALE_TAGS:
            self.delete_stale_tags()
        elif option == STR_DELETE_UNTAGGED_IMAGES:
            self.delete_untagged_images()
        elif option == STR_DELETE_TAGS_WITH_PREFIX:
            self.delete_tags_with_prefix()
        elif option == STR_DELETE_TAGS_WITH_SUFFIX:
            self.delete_tags_with_suffix()
        elif option == STR_BACK:
            self.manage_repositories()
        elif option == STR_EXIT:
            sys.exit()

        self.repository_menu()

    def list_last_tags(self, quiet: bool = False) -> None:
        """
        List the last tags for the repository.
        :param quiet: Quiet mode
        :return: None
        """
        page_size = 1000
        tags_no_str = input(f"Enter the number of tags to fetch (default: {page_size}): ")
        if tags_no_str:
            tags_no = int(tags_no_str)
        else:
            tags_no = page_size
        total_pages = (tags_no + page_size - 1) // page_size  # Calculate the total number of pages needed
        tags = []
        for page in range(1, total_pages + 1):
            print(f"Fetching tags page: {page}")
            page_size = min(1000, tags_no - len(tags))
            response = call_api("GET", f"repositories/{self.owner}/{self.repository}/tags",
                                auth=self.auth, params=f"page_size={page_size}&page={page}").json()
            if not response:
                print("No more tags available.")
                break

            new_tags = response['results']
            if not new_tags:
                break
            tags.extend(new_tags)

            if len(tags) >= tags_no or response.get('next') is None:
                break

        # Sort tags by last updated date and show them as a MD table
        tags.sort(key=lambda tag: tag['last_updated'], reverse=True)
        self.tags = tags
        total_space = 0
        if not quiet and tags:
            table = []
            for tag in tags:
                table.append([tag['name'], bytes_to_human_readable(tag['full_size']),
                              get_date_str(tag['tag_last_pushed']), get_date_str(tag.get('tag_last_pulled'))])
                total_space += tag['full_size']
            print(f"{self.owner}/{self.repository} tags:")
            print_markdown_table("Tag | Size | Last pushed | Last pulled", table)
            print(f"Total space: {bytes_to_human_readable(total_space)}")
            input("Press Enter to return to the repository menu...")

    def save_tags_file(self) -> None:
        """
        Save the retrieved tags to a file.
        :return: None
        """
        if self.tags is None:
            print("Need to list tags first.")
            self.list_last_tags(quiet=True)

        filename = input("Enter the filename to save the tags: ")
        with open(filename, 'w') as f:
            json.dump(self.tags, f, indent=4)

        print(f"Tags saved to {filename}")
        input("Press Enter to return to the repository menu...")


    def delete_stale_tags(self) -> None:
        """
        Delete stale tags that haven't been pulled or pushed in a specified number of days.
        TODO: Waiting to be implemented in the API
        Conditions for deletion:
        - tag is pushed more than set amount of days, but it doesn't end with "latest".
        - tag hasn't been pulled in set amount of days, but it doesn't end with "latest",
          that includes also "Never" pulled.
        :return: None
        """
        if self.tags is None:
            print("Need to list tags first.")
            self.list_last_tags(quiet=True)

        # ask for the number of days
        days = int(input("Enter the number of days: "))
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
        print(f"Deleting tags older than {get_date_str(cutoff_date)}")
        total_freed_space = 0

        # delete tags older than the cutoff date
        for tag in self.tags:
            if tag['name'].endswith('latest'):
                continue

            # check if the tag was pulled
            last_pulled = tag.get('tag_last_pulled')
            if last_pulled == 'Never':
                last_pulled_date = None
            else:
                last_pulled_date = get_datetime(last_pulled)

            # check if the tag was pushed
            last_pushed = tag.get('tag_last_pushed')
            if last_pushed == 'Never':
                last_pushed_date = None
            else:
                last_pushed_date = get_datetime(last_pushed)

            # check if the tag is older than the cutoff date
            if ((last_pushed_date and last_pushed_date < cutoff_date) or
                    (last_pulled_date and last_pulled_date < cutoff_date)):
                print(f'Deleting tag: {tag["name"]}, '
                      f'last pushed {get_date_str(last_pushed_date)}, '
                      f'last pulled {get_date_str(last_pulled_date)}, '
                      f'size {bytes_to_human_readable(tag["full_size"])}')
                total_freed_space += tag['full_size']
                self.delete_tag(tag['name'])

        print(f"Total freed space: {bytes_to_human_readable(total_freed_space)}")
        input("Press Enter to return to the repository menu...")

    def delete_untagged_images(self) -> None:
        """
        Delete untagged images from the repository.
        TODO: Waiting to be implemented in the API
        :return: None
        """
        if self.tags is None:
            print("Need to list tags first.")
            self.list_last_tags(quiet=True)

        # ask for the number of days
        total_freed_space = 0
        for tag in self.tags:
            if tag.get('status') == 'active':
                continue

            # check if the tag is untagged
            if not tag['name']:
                print(f"fDeleting untagged image: {tag['digest']}, "
                      f"last pushed {get_date_str(tag['tag_last_pushed'])}, "
                      f"last pulled {get_date_str(tag.get('tag_last_pulled'))}, "
                      f"size {bytes_to_human_readable(tag['full_size'])}")
                total_freed_space += tag['full_size']
                self.delete_tag(tag['digest'])

        print(f"Total freed space: {bytes_to_human_readable(total_freed_space)}")
        input("Press Enter to return to the repository menu...")

    def delete_tags_with_prefix(self) -> None:
        """
        Delete tags with a specified prefix.
        TODO: Waiting to be implemented in the API
        :return: None
        """
        if self.tags is None:
            print("Need to list tags first.")
            self.list_last_tags(quiet=True)

        # ask for the prefix
        prefix = input("Enter the prefix for tags to delete: ")
        total_freed_space = 0

        # delete tags with the specified prefix
        for tag in self.tags:
            if tag['name'].startswith(prefix):
                self.delete_tag(tag['name'])
                total_freed_space += tag['full_size']

        print(f"Total freed space: {bytes_to_human_readable(total_freed_space)}")
        input("Press Enter to return to the repository menu...")

    def delete_tags_with_suffix(self) -> None:
        """
        Delete tags with a specified suffix.
        TODO: Waiting to be implemented in the API
        :return: None
        """
        if self.tags is None:
            print("Need to list tags first.")
            self.list_last_tags(quiet=True)

        # ask for the suffix
        suffix = input("Enter the suffix for tags to delete: ")
        total_freed_space = 0

        # delete tags with the specified suffix
        for tag in self.tags:
            if tag['name'].endswith(suffix):
                self.delete_tag(tag['name'])
                total_freed_space += tag['full_size']

        print(f"Total freed space: {bytes_to_human_readable(total_freed_space)}")
        input("Press Enter to return to the repository menu...")

    def delete_tag(self, tag: str) -> None:
        """
        Delete a tag from the repository.
        TODO: Waiting to be implemented in the API
        :param tag: Tag to delete
        :return: None
        """
        response = call_api("DELETE", f"repositories/{self.owner}/{self.repository}/tags/{tag}",
                            auth=(self.username, '5f98e1cb-71b1-441e-95db-be4ec32a5324')
                            )
        if response.status_code == 204:
            print(f"Deleted tag: {tag}")
        else:
            print(f"Failed to delete tag: {tag}")

    def manage_organization(self) -> None:
        """
        Display organization administration menu.
        :return: None
        """
        self.verify_organization()
        title = f"Manage organization {self.owner}:"
        options = [
            STR_MANAGE_USERS,
            STR_MANAGE_TEAMS_GROUPS,
            STR_GROUP_MEMBERSHIP,
            STR_BACK,
            STR_EXIT
        ]
        option, index = pick(options, title)

        if option == STR_MANAGE_USERS:
            self.manage_users()
        elif option == STR_MANAGE_TEAMS_GROUPS:
            self.manage_teams_groups()
        elif option == STR_GROUP_MEMBERSHIP:
            self.group_membership()
        elif option == STR_BACK:
            self.docker_menu()
        elif option == STR_EXIT:
            sys.exit()

        self.manage_organization()

    def manage_users(self) -> None:
        """
        Display manage users menu.
        :return: None
        """
        self.verify_organization()
        title = f"{STR_MANAGE_USERS}:"
        options = [
            STR_LIST_MEMBERS,
            STR_INVITE_USER,
            STR_UPDATE_MEMBER_ROLE,
            STR_REMOVE_MEMBER,
            STR_BACK,
            STR_EXIT
        ]
        option, index = pick(options, title)

        if option == STR_LIST_MEMBERS:
            self.list_members()
        elif option == STR_INVITE_USER:
            self.invite_user()
        elif option == STR_UPDATE_MEMBER_ROLE:
            self.update_member_role()
        elif option == STR_REMOVE_MEMBER:
            self.remove_member()
        elif option == STR_BACK:
            self.manage_organization()
        elif option == STR_EXIT:
            sys.exit()

        self.manage_users()

    def manage_teams_groups(self) -> None:
        """
        Display manage teams/groups menu.
        :return: None
        """
        self.verify_organization()
        title = "Manage Teams/Groups:"
        options = [
            STR_LIST_GROUPS,
            STR_CREATE_GROUP,
            STR_UPDATE_GROUP_DETAILS,
            STR_DELETE_GROUP,
            STR_BACK,
            STR_EXIT
        ]
        option, index = pick(options, title)

        if option == STR_LIST_GROUPS:
            self.list_groups()
        elif option == STR_CREATE_GROUP:
            self.create_group()
        elif option == STR_UPDATE_GROUP_DETAILS:
            self.update_group_details()
        elif option == STR_DELETE_GROUP:
            self.delete_group()
        elif option == STR_BACK:
            self.manage_organization()
        elif option == STR_EXIT:
            sys.exit()

        self.manage_teams_groups()

    def group_membership(self) -> None:
        """
        Display group membership menu.
        :return: None
        """
        self.verify_organization()
        title = "Group Membership:"
        options = [
            STR_LIST_GROUP_MEMBERS,
            STR_ADD_MEMBER_TO_GROUP,
            STR_REMOVE_MEMBER_FROM_GROUP,
            STR_BACK,
            STR_EXIT
        ]
        option, index = pick(options, title)

        if option == STR_LIST_GROUP_MEMBERS:
            self.list_group_members()
        elif option == STR_ADD_MEMBER_TO_GROUP:
            self.add_member_to_group()
        elif option == STR_REMOVE_MEMBER_FROM_GROUP:
            self.remove_member_from_group()
        elif option == STR_BACK:
            self.manage_organization()
        elif option == STR_EXIT:
            sys.exit()

        self.group_membership()

    def list_members(self) -> None:
        """
        List members of the organization.
        :return: None
        """
        self.verify_organization()
        response = call_api("GET", f"orgs/{self.owner}/members", headers=self.headers)
        members = response.json()['results']
        members.sort(key=lambda member: member['username'])
        table = [[member['username'], member['email'], member['role'], ', '.join(member['groups'])] for member in
                 members]
        print(f"{self.owner} organization members:")
        print_markdown_table("Username | Email | Role | Groups", table)
        input("Press Enter to return to the manage users menu...")

    def invite_user(self) -> None:
        """
        Invite a user to the organization.
        :return: None
        """
        self.verify_organization()
        email_username = input("Enter the email or username to invite: ")
        role = input("Enter the role for the user (member/admin): ")
        team = input("Enter the team name: ")
        payload = {
            "org": self.owner,
            "team": team,
            "role": role,
            "invitees": [email_username]
        }
        response = call_api("POST", f"invites/bulk", payload=payload, headers=self.headers)
        print(f"Invitation sent to {email_username}.")
        input("Press Enter to return to the manage users menu...")

    def update_member_role(self) -> None:
        """
        Update the role of a member in the organization.
        :return: None
        """
        self.verify_organization()
        username = input("Enter the username of the member to update: ")
        role = input("Enter the new role for the member (member/admin): ")
        payload = {
            "role": role
        }
        response = call_api("PUT", f"orgs/{self.owner}/members/{username}", payload=payload, headers=self.headers)
        print(f"Updated role for {username} to {role}.")
        input("Press Enter to return to the manage users menu...")

    def remove_member(self) -> None:
        """
        Remove a member from the organization.
        :return: None
        """
        self.verify_organization()
        username = input("Enter the username of the member to remove: ")
        response = call_api("DELETE", f"orgs/{self.owner}/members/{username}", headers=self.headers)
        print(f"Removed member {username} from the {self.owner} organization.")
        input("Press Enter to return to the manage users menu...")

    def list_groups(self) -> None:
        """
        List groups in the organization.
        :return: None
        """
        self.verify_organization()
        response = call_api("GET", f"orgs/{self.owner}/groups", headers=self.headers)
        groups = response.json()['results']
        table = [[group['name'], group['description'], str(group['member_count'])] for group in groups]
        print(f"{self.owner} organization groups:")
        print_markdown_table("Name | Description | Member Count", table)
        input("Press Enter to return to the manage teams/groups menu...")

    def create_group(self) -> None:
        """
        Create a new group in the organization.
        :return: None
        """
        self.verify_organization()
        name = input("Enter the name of the new group: ")
        description = input("Enter the description of the new group: ")
        payload = {
            "name": name,
            "description": description
        }
        response = call_api("POST", f"orgs/{self.owner}/groups", payload=payload, headers=self.headers)
        print(f"Created group {name}.")
        input("Press Enter to return to the manage teams/groups menu...")

    def update_group_details(self) -> None:
        """
        Update the details of a group in the organization.
        :return: None
        """
        self.verify_organization()
        group_name = input("Enter the name of the group to update: ")
        url = f"{DOCKER_HUB_API}//"
        response = call_api("GET", f"orgs/{self.owner}/groups/{group_name}", headers=self.headers)
        group = response.json()
        name = input(f"Enter the new name for the group (current: {group['name']}): ") or group['name']
        description = input(f"Enter the new description for the group (current: {group['description']}): ") or group[
            'description']
        payload = {
            "name": name,
            "description": description
        }
        response = call_api("PATCH", f"orgs/{self.owner}/groups/{group_name}", headers=self.headers, payload=payload)
        print(f"Updated group {group_name}.")
        input("Press Enter to return to the manage teams/groups menu...")

    def delete_group(self) -> None:
        """
        Delete a group from the organization.
        :return: None
        """
        self.verify_organization()
        group_name = input("Enter the name of the group to delete: ")
        url = f"{DOCKER_HUB_API}/"
        response = call_api("DELETE", f"orgs/{self.owner}/groups/{group_name}", headers=self.headers)
        print(f"Deleted group {group_name}.")
        input("Press Enter to return to the manage teams/groups menu...")

    def list_group_members(self) -> None:
        """
        List members of a group in the organization.
        :return: None
        """
        self.verify_organization()
        group_name = input("Enter the name of the group: ")
        response = call_api("GET", f"orgs/{self.owner}/groups/{group_name}/members", headers=self.headers)
        members = response.json()['results']
        table = [[member['email'], member['username']] for member in members]
        print(f"{self.owner} organization group {group_name} members:")
        print_markdown_table("Email | Username", table)
        input("Press Enter to return to the group membership menu...")

    def add_member_to_group(self) -> None:
        """
        Add a member to a group in the organization.
        :return: None
        """
        self.verify_organization()
        group_name = input("Enter the name of the group: ")
        username = input("Enter the username of the member to add: ")
        payload = {
            "member": username
        }
        response = call_api("POST", f"orgs/{self.owner}/groups/{group_name}/memberships", payload=payload, headers=self.headers)
        print(f"Added {username} to group {group_name}.")
        input("Press Enter to return to the group membership menu...")

    def remove_member_from_group(self) -> None:
        """
        Remove a member from a group in the organization.
        :return: None
        """
        self.verify_organization()
        group_name = input("Enter the name of the group: ")
        username = input("Enter the username of the member to remove: ")
        response = call_api("DELETE", f"orgs/{self.owner}/groups/{group_name}/members/{username}", headers=self.headers)
        print(f"Removed {username} from group {group_name}.")
        input("Press Enter to return to the group membership menu...")
