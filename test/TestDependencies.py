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


    def clone_and_load_config(self,upstream_path,local_dir):

        git.clone(upstream_path,self.output_dir,local_dir,verbosity=-1)

        project_path = join(self.output_dir,local_dir)

        project_manifest = join(project_path,'abaci.toml')

        config, config_dir = load_config(project_manifest, echo=False)

        return project_path, config, config_dir
        

    def test_simple_dependencies(self):
        """
            Test simple dependency hierarchy

            root-->dep1
                -->dep3-->dep2
                
        """

        self.new_temp_project(name="dep1",version="v1",deps=None)
        self.new_temp_project(name="dep2",version="v2",
                              deps=[self.temp_dep(name="dep3",version="v3")])
        self.new_temp_project(name="dep3",version="v3",deps=None)

        temp_upstream = self.new_temp_project(name="root",version="v1",
                              deps=[self.temp_dep(name="dep1",version="v1"),
                                    self.temp_dep(name="dep2",version="v2")
                              ])

        project_path, config, config_dir = self.clone_and_load_config(temp_upstream,'root')

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

            # Check correct versions of dependencies were checked-out
            self.assertEquals(git.get_tag(join('dependencies','dep1')), 'v1')
            self.assertEquals(git.get_tag(join('dependencies','dep2')), 'v2')
            self.assertEquals(git.get_tag(join('dependencies','dep3')), 'v3')


    def test_circular_dependencies(self):
        """
            Test mutually dependent projects

            project1<-->project2

        """

        project1 = self.new_temp_project(name="project1",version="v1",
                              deps=[self.temp_dep(name="project2",version="v1")])

        project2 = self.new_temp_project(name="project2",version="v1",
                              deps=[self.temp_dep(name="project1",version="v1")])

        if verbose:
            verbosity = 1
        else:
            verbosity = 0

        # Try project 1
        project_path, config, config_dir = self.clone_and_load_config(project1,'project1')
        
        with cwd(project_path):

            fetch_dependencies(config, config_dir, verbosity)

            # Check dependencies were fetched
            self.assertTrue(isdir('dependencies'))
            self.assertTrue(isdir(join('dependencies','project2')))
            self.assertTrue(exists(join('dependencies','project2','abaci.toml')))

        # Try project 2
        project_path, config, config_dir = self.clone_and_load_config(project2,'project2')
        
        with cwd(project_path):

            fetch_dependencies(config, config_dir, verbosity)

            # Check dependencies were fetched
            self.assertTrue(isdir('dependencies'))
            self.assertTrue(isdir(join('dependencies','project1')))
            self.assertTrue(exists(join('dependencies','project1','abaci.toml')))


    def test_duplicate_dependencies(self):
        """
            Test dependency hierarchy with a duplicate dependent

            root-->dep1-->dep3@v1
                -->dep2-->dep3@v2
                
            Both dep1 and dep2 depend on dep3 with differing versions:
            priority is given to the higher/earlier dependent. In this
            case dep1 is listed first, so dep3 should be taken at v1 not v2.

        """

        self.new_temp_project(name="dep1",version="v1",
                              deps=[self.temp_dep(name="dep3",version="v1")])
        self.new_temp_project(name="dep2",version="v1",
                              deps=[self.temp_dep(name="dep3",version="v2")])
        self.new_temp_project(name="dep3",version="v1",deps=None)

        temp_upstream = self.new_temp_project(name="root",version="v1",
                              deps=[self.temp_dep(name="dep1",version="v1"),
                                    self.temp_dep(name="dep2",version="v1")
                              ])

        project_path, config, config_dir = self.clone_and_load_config(temp_upstream,'root')

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

            # Check correct version of dep3 has been fetched
            self.assertEquals(git.get_tag(join('dependencies','dep3')), 'v1')


    def test_dependency_update(self):
        """
            Test updating of a dependency

            root-->dep1@v1
            
        """

        self.new_temp_project(name="dep1",version="v1",deps=None)
        self.new_temp_project(name="dep1",version="v2",deps=None)

        temp_upstream = self.new_temp_project(name="root",version="v1",
                              deps=[self.temp_dep(name="dep1",version="v1")])

        project_path, config, config_dir = self.clone_and_load_config(temp_upstream,'root')

        if verbose:
            verbosity = 1
        else:
            verbosity = 0

        with cwd(project_path):

            fetch_dependencies(config, config_dir, verbosity)

            # Check dependency was fetched
            self.assertTrue(isdir('dependencies'))
            self.assertTrue(isdir(join('dependencies','dep1')))
            self.assertEquals(git.get_tag(join('dependencies','dep1')), 'v1')


        # Now specify a newer version of dep1
        config['dependency'][0]['version'] = 'v2'

        with cwd(project_path):

            fetch_dependencies(config, config_dir, verbosity)

            # Check dependency was updated
            self.assertEquals(git.get_tag(join('dependencies','dep1')), 'v2')


    def test_invalid_dependency(self):
        """
            Test exception for an invalid dependency
            When 'name' field does not match in parent and child project manifests

            root-->dep1
            
        """

        self.new_temp_project(name="dep1",version="v1",deps=None)

        temp_upstream = self.new_temp_project(name="root",version="v1",
                              deps=[self.temp_dep(name="dep1",version="v1")])

        project_path, config, config_dir = self.clone_and_load_config(temp_upstream,'root')

        config['dependency'][0]['name'] = 'wrong_name'

        if verbose:
            verbosity = 1
        else:
            verbosity = 0

        with self.assertRaises(Exception):

            fetch_dependencies(config, config_dir, verbosity)

