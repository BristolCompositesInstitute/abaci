import unittest
import tempfile
import os

from AbaciUnitTestSuite import AbaciUnitTestSuite

class TestConfig(AbaciUnitTestSuite):

    def test_init_config(self):
        """
        Test that the config produced by abaci init is a valid config
        """

        from abaci.config import init_new_config, read_config_file, parse_config

        fh,config_file = tempfile.mkstemp()
        os.close(fh)

        usub_file = 'a.f'
        output = 'b'

        init_new_config(config_file,user_sub_file=usub_file,output=output,full=True,bare=False)

        config_str = read_config_file(config_file)

        config = parse_config(config_str)

        self.assertEqual(usub_file,config['user-sub-file'])
        self.assertEqual(output,config['output'])

