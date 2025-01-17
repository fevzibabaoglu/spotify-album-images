import requests
import os
from dotenv import load_dotenv


# Load .env file
load_dotenv()


class Utils:
    @staticmethod
    def get_or_ask_env(env_var_name):
        """Retrieve an environment variable or ask the user for its value."""
        value = os.getenv(env_var_name)
        if not value:
            value = input(f'Enter value for {env_var_name}: ').strip()
        return value

    @staticmethod
    def get(url, headers=None):
        """Make a GET request and return the response."""
        try:
            response = requests.get(url, headers=headers)
            return response
        except requests.RequestException as e:
            raise RuntimeError(f'GET request failed: {e}')

    @staticmethod
    def post(url, data=None, headers=None):
        """Make a POST request and return the response."""
        try:
            response = requests.post(url, data=data, headers=headers)
            return response
        except requests.RequestException as e:
            raise RuntimeError(f'POST request failed: {e}')

    @staticmethod
    def handle_error(response, message):
        """Handle API errors and print detailed information."""
        error_details = response.text
        raise RuntimeError(f'{message}\nHTTP Status: {response.status_code}\nDetails: {error_details}')
