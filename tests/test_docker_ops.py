import unittest
from velez.docker_ops import DockerOperations
from unittest.mock import patch, MagicMock

class TestDockerOperations(unittest.TestCase):

    @patch('docker.from_env')
    def setUp(self, mock_docker):
        self.mock_velez = MagicMock()
        self.docker_ops = DockerOperations(self.mock_velez)

    @patch('builtins.input', return_value='username')
    @patch('builtins.input', return_value='password')
    def test_login(self, mock_input_username, mock_input_password):
        self.docker_ops.login()
        self.docker_ops.client.login.assert_called_with(username='username', password='password')

    def test_list_repositories_menu(self):
        with patch('velez.docker_ops.pick', return_value=("List last pushed tags", 0)):
            self.docker_ops.list_repositories_menu()
            # Add assertions for list_last_pushed_tags

if __name__ == '__main__':
    unittest.main()
