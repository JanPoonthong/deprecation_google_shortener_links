"""DOCS"""
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()


class RequestHandler:
    """Handle HTTP requests"""

    @staticmethod
    def safe_request_get(url: str, allow_redirects=True, **kwargs):
        """Safely get request to url"""

        headers = kwargs.get("headers", {})

        try:
            response = requests.get(
                url, headers=headers, allow_redirects=allow_redirects, timeout=3
            )
        except requests.exceptions.Timeout as error:
            print(f"ERROR: Timed out for {url}")
            raise Exception(error)

        if response is None:
            raise requests.exceptions.RequestException("Error: response is None")

        return response

    @staticmethod
    def safe_request_post(url: str, allow_redirects=True, **kwargs):
        """Safely post request to url"""

        headers = kwargs.get("headers", {})
        data = kwargs.get("data", {})
        data = json.dumps(data)

        try:
            response = requests.post(
                url,
                headers=headers,
                allow_redirects=allow_redirects,
                timeout=3,
                data=data,
            )
        except requests.exceptions.Timeout as error:
            print(f"ERROR: Timed out for {url}")
            raise Exception(error)

        if response is None:
            raise requests.exceptions.RequestException("Error: response is None")

        return response


class GitHubSearcher:
    """Handle GitHub code searching"""

    def __init__(self, token):
        self.token = token

    @staticmethod
    def read_file():
        """DOCS"""
        file_name = "response.json"
        try:
            with open(file_name, "r", encoding="utf-8") as file:
                json_data = json.load(file)
        except Exception as error:
            print(f"ERROR: writing on {file_name}")
            raise Exception(error)
        return json_data["items"]

    @staticmethod
    def write_to_file(file_name, response):
        """DOCS"""
        try:
            with open(file_name, "w") as file:
                file.write(response.text)
        except Exception as error:
            print(f"ERROR: writing on {file_name}")
            raise Exception(error)

    def github_code_search(self):
        """Search goo.gl on GitHub"""
        url = "https://api.github.com/search/code?q=https://goo.gl"

        headers = {"Authorization": f"Token {self.token}"}

        response = RequestHandler.safe_request_get(url, headers=headers)
        self.write_to_file("code_search_response_file.json", response)
        return response.json()

    @staticmethod
    def get_destination_url(url) -> str:
        """Get the 'location' from response header to get final destination url"""

        response = RequestHandler.safe_request_get(url, allow_redirects=False)

        location = response.headers["location"]
        return location

    def fork(self, owner_name, repo_name) -> bool:
        """DOCS"""

        url = f"https://api.github.com/repos/{owner_name}/{repo_name}/forks"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        data = {
            "name": f"{repo_name}",
            "default_branch_only": "true",
        }

        response = RequestHandler.safe_request_post(url, headers=headers, data=data)
        self.write_to_file(f"fork_response_{repo_name}.json", response)

        response_json = response.json()

        if response.status_code == 202:
            print(
                f"Successfully fork repo name {repo_name}, here is the url: {response_json['html_url']}"
            )
            return True

        print(f"ERROR: {response.text}")
        print(f"Can't fork repo name {repo_name}")
        return False

    def delete_repo():
        pass

    @staticmethod
    def parse_url(url) -> tuple:
        """This function parse url to get repo_name and owner_name for fork()"""

        owner_name = url.split("/")[3]
        repo_name = url.split("/")[4]

        return owner_name, repo_name


def main():
    """Starting of the program"""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("GITHUB_TOKEN is not set in the environment variables.")
        return

    searcher = GitHubSearcher(token)
    print(searcher.github_code_search())


main()
