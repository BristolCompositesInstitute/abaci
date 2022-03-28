import tempfile
import os
import sys
import unittest

from abaci.cli import logging

verbose = False
fast_mode = False
abaqus_checked = False
abaqus_enabled = None

class AbaciUnitTestSuite(unittest.TestCase):

    def setUp(self):
        """Set up logging and temporary directories for output"""

        global verbose

        if verbose:
            logging.basicConfig(level=logging.DEBUG,stream=sys.stdout)
            log = logging.getLogger('abaci')

        self.output_dir = tempfile.mkdtemp()
        self.root_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..')


    @staticmethod
    def abaqus_available():
        """Test if abaqus command is available for tests"""

        from abaci.utils import system_cmd, system_cmd_wait

        global fast_mode
        global abaqus_checked
        global abaqus_enabled

        if not abaqus_checked:

            if fast_mode:

                abaqus_enabled = False

            else:

                fh,tempf = tempfile.mkstemp()
                os.close(fh)

                try:
                    p,ofile,efile = system_cmd(['abaqus', 'information=versions'],output=tempf)
                    stat = system_cmd_wait(p,verbosity=-1)

                except:
                    stat = 1
                    
                abaqus_enabled = stat == 0

            abaqus_checked = True
        
        return abaqus_enabled