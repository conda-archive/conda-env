import unittest
from mock import MagicMock, patch
from conda_env.utils.uploader import Uploader


class TestUploader(unittest.TestCase):
    def setUp(self):
        self.valid_attr = ['name', 'file', 'version', 'summary']

    @patch('conda_env.utils.uploader.get_binstar')
    def test_user_logged_in(self, get_binstar_mock):
        binstar_user = MagicMock()
        get_binstar_mock.return_value = binstar_user

        client = Uploader(*self.valid_attr)
        self.assertEqual(client.user, binstar_user.user())


if __name__ == '__main__':
    unittest.main()
