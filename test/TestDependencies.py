import tempfile
import os
from os.path import join, isdir, exists

from AbaciUnitTestSuite import AbaciUnitTestSuite, verbose

from abaci.config import load_config
from abaci.utils import cwd, copydir, mkdir
from abaci.dependencies import fetch_dependencies
from abaci import git_utils as git

class TestDependencies(AbaciUnitTestSuite):

    def temp_dep(self,name,version):
        """Helper to return reference to temporary project as dependency"""

        return {'name': name,
                'git': join(self.output_dir,name+".git"),
                'version': version}


    def new_temp_project(self,name,version,deps=None):
        """Create a new temporary git repo with an abaci project for testing"""

        project_upstream = join(self.output_dir,name+".git")

        if not os.path.exists(project_upstream):

            mkdir(project_upstream)

            git.init_bare(project_upstream)

        # Clone the upstream to modify it
        temp_dir = tempfile.mkdtemp()

        git.clone(project_upstream,temp_dir,name,verbosity=-1)

        project_path = join(temp_dir,name)

        project_manifest = join(project_path,'abaci.toml')

        if not os.path.exists(project_manifest):

            with open(project_manifest,'w') as f:

                f.write('name = "{name}"\n'.format(name=name))

                if deps:

                    for dep in deps:

                        f.write('[[dependency]]\n')
                        f.write('name = "{name}"\n'.format(name=dep['name']))
                        f.write("git = '{path}'\n".format(path=dep['git']))
                        f.write('version = "{ver}"\n\n'.format(ver=dep['version']))

            git.add_and_commit(project_path,'Initial commit')

        else:

            git.add_and_commit(project_path,'Another commit')

        git.add_tag(project_path,version)

        git.push(project_path)

        return project_upstream


    def test_dependency_fetching(self):
        """
            Test dependency fetching
        """

        self.new_temp_project(name="dep1",version="v1",deps=None)
        self.new_temp_project(name="dep2",version="v1",deps=None)
        self.new_temp_project(name="dep3",version="v1",
                              deps=[self.temp_dep(name="dep2",version="v1")])

        temp_upstream = self.new_temp_project(name="root",version="v1",
                              deps=[self.temp_dep(name="dep1",version="v1"),
                                    self.temp_dep(name="dep3",version="v1")
                              ])

        git.clone(temp_upstream,self.output_dir,'root',verbosity=-1)

        project_path = join(self.output_dir,'root')

        project_manifest = join(project_path,'abaci.toml')

        config, config_dir = load_config(project_manifest, echo=False)

        if verbose:
            verbosity = 1
        else:
            verbosity = 0

        with cwd(project_path):

            fetch_dependencies(config, config_dir, verbosity)

            # Check dependencies were fetched
            self.assertTrue(isdir('dependencies'))
            self.assertTrue(isdir(join('dependencies','dep1')))
            self.assertTrue(isdir(join('dependencies','dep2')))
            self.assertTrue(isdir(join('dependencies','dep3')))
            self.assertTrue(exists(join('dependencies','dep1','abaci.toml')))
            self.assertTrue(exists(join('dependencies','dep2','abaci.toml')))
            self.assertTrue(exists(join('dependencies','dep3','abaci.toml')))