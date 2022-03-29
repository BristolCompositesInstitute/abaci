from os.path import join, isdir, exists

from AbaciUnitTestSuite import AbaciUnitTestSuite, verbose

from abaci.config import load_config
from abaci.utils import cwd, copydir, mkdir
from abaci.dependencies import fetch_dependencies

class TestDependencies(AbaciUnitTestSuite):

    def test_dependency_fetching(self):
        """
            Test dependency fetching
        """

        test_project_path = join(self.root_dir,'test','data','test-dep')

        copydir(test_project_path,self.output_dir)

        config_file = join(self.output_dir,'abaci.toml')

        config, config_dir = load_config(config_file,echo=False)

        if verbose:
            verbosity = 1
        else:
            verbosity = 0

        with cwd(self.output_dir):

            fetch_dependencies(config, config_dir, verbosity)

            # Check dependencies were fetched
            self.assertTrue(isdir('dependencies'))
            self.assertTrue(isdir(join('dependencies','test-dep1')))
            self.assertTrue(isdir(join('dependencies','test-dep2')))
            self.assertTrue(isdir(join('dependencies','test-dep3')))
            self.assertTrue(exists(join('dependencies','test-dep1','abaci.toml')))
            self.assertTrue(exists(join('dependencies','test-dep2','abaci.toml')))
            self.assertTrue(exists(join('dependencies','test-dep3','abaci.toml')))