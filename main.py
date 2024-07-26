"DOCS"
import os
import requests
from dotenv import load_dotenv

load_dotenv()


class RequestHadler:
    "Handle HTTP requests"
    @staticmethod
    def safe_request(url: str, headers={}, allow_redirects=True):
        "Safely request a url"

        response = None
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


class GitHubSearcher:
    "Handle GitHub code searching"

    def __init__(self, token):
        self.token = token

    @staticmethod
    def write_to_file(response):
        "DOCS"
        file_name = "response.json"
        try:
            with open(file_name, 'w') as file:
                file.write(response.text)
        except Exception as error:
            print(f"ERROR: writing on {file_name}")
            raise Exception(error)

    def github_code_search(self):
        "Search goo.gl on GitHub"
        url = "https://api.github.com/search/code?q=https://goo.gl"

        headers = {"Authorization": f"Token {self.token}"}

        response = RequestHadler.safe_request(url, headers=headers)
        self.write_to_file(response)
        return response.json()

    @staticmethod
    def get_destination_url(url) -> str:
        "Get the 'location' from response header to get final destination url"

        response = RequestHadler.safe_request(url, allow_redirects=False)

        location = response.headers["location"]
        return location


def main():
    "Starting of the program"
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("GITHUB_TOKEN is not set in the environment variables.")
        return

    searcher = GitHubSearcher(token)
    print(searcher.github_code_search())


main()
