import sys
import os
import unittest

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")

import AbaciUnitTestSuite


if __name__ == '__main__':

    if '--fast' in sys.argv:
        sys.argv.remove('--fast')
        AbaciUnitTestSuite.fast_mode = True

    if '-vv' in sys.argv:
        AbaciUnitTestSuite.verbose =True

    from TestAbaqusJob import TestAbaqusJob

    unittest.main()