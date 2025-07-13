import unittest
from src.launcher import Launcher

class TestLauncher(unittest.TestCase):

    def setUp(self):
        self.launcher = Launcher()

    def test_add_script(self):
        self.launcher.add_script('test_script.py')
        self.assertIn('test_script.py', self.launcher.scripts)

    def test_run_script(self):
        self.launcher.add_script('test_script.py')
        output = self.launcher.run('test_script.py')
        self.assertIsNotNone(output)

if __name__ == '__main__':
    unittest.main()