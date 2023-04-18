import requests
from io import BytesIO
from typing import Tuple, Union
from urllib.parse import urljoin

class GogglesApi:
    """A Python library for interacting with the Goggles API."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url

    def extract_text(self, filename: str, file_input: Union[bytes, BytesIO]) -> Tuple[int, Union[dict, str]]:
        """
        Extract text from a given file.

        :param filename: The name of the file.
        :param file_input: A byte array or a file pointer (BytesIO) containing the file data.
        :return: A tuple containing the response status code and either the response data or an error message.
        """
        url = urljoin(self.base_url, "/api/Extract/text")
        
        if isinstance(file_input, bytes):
            file = BytesIO(file_input)
        else:
            file = file_input
        
        files = {'file': (filename, file)}

        try:
            response = requests.post(url, files=files)
        except requests.RequestException as e:
            return -1, str(e)

        if response.status_code == 200:
            return response.status_code, response.json()
        else:
            return response.status_code, response.reason

    def extract_content_type(self, extension: str) -> Tuple[int, Union[dict, str]]:
        """
        Get the content type for a given file extension.

        :param extension: The file extension.
        :return: A tuple containing the response status code and either the response data or an error message.
        """
        url = urljoin(self.base_url, "/api/Extract/contentType")
        params = {'extension': extension}

        try:
            response = requests.get(url, params=params)
        except requests.RequestException as e:
            return -1, str(e)

        if response.status_code == 200:
            return response.status_code, response.json()
        else:
            return response.status_code, response.reason

# Usage example:
if __name__ == "__main__":
    base_url = "https://goggles.magico13.net"
    goggles_api = GogglesApi(base_url)
    
    # Example usage for the 'extract_text' API
    filename = "example.jpg"
    with open(filename, "rb") as file:
        status_code, response_data = goggles_api.extract_text(filename, file)
    print(f"Status code: {status_code}")
    print(f"Response data: {response_data}")
    
    # Example usage for the 'extract_content_type' API
    extension = "pdf"
    status_code, response_data = goggles_api.extract_content_type(extension)
    print(f"Status code: {status_code}")
    print(f"Response data: {response_data}")
