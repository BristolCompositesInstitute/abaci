import unittest
import tempfile
import os

from AbaciUnitTestSuite import AbaciUnitTestSuite

class TestAbaqusJob(AbaciUnitTestSuite):

    def get_dummy_check(self):
        """
            Returns a valid job['checks'] config for testing purposes
        """
        return {'fields': ['SDV1','SDV2'],
                'reference':'ref.pkl',
                'steps': ['Step-1']}


    def get_dummy_job(self):
        """
            Returns a valid job config for testing purposes
        """

        job_base_name = 'job-file'

        job = {}
        job['job-file'] = job_base_name + '.inp'
        job['include'] = ['extra.inp']
        job['name'] = 'job-name'
        job['abq-flags'] = []
        job['check'] = self.get_dummy_check()
        job['mp-mode'] = 'threads'
        job['post-process'] = None
        job['cluster'] = None
        
        return job, job_base_name


    def test_job_constructor_config(self):
        """
            Test the AbaqusJob constructor using job config input
        """
        from abaci.AbaqusJob import AbaqusJob

        job_config, job_base_name = self.get_dummy_job()

        job = AbaqusJob(self.output_dir,job=job_config)

        # Check config attributes are transferred correctly
        self.assertEqual(job.name,job_config['name'])
        self.assertEqual(job.include,job_config['include'])
        self.assertEqual(job.checks,job_config['check'])
        self.assertEqual(job.job_file,job_config['job-file'])
        self.assertEqual(job.mp_mode,job_config['mp-mode'])
        self.assertEqual(job.local_job_name,job_base_name)


    def test_job_constructor_file(self):
        """
            Test the AbaqusJob constructor using job file input
        """
        from abaci.AbaqusJob import AbaqusJob

        job_name = 'myjob'
        job = AbaqusJob(self.output_dir,job_file=job_name+'.inp')

        # Check default attributes are set correctly
        self.assertEqual(job.name,job_name+'.inp')
        self.assertEqual(job.include,[])
        self.assertEqual(job.checks,None)
        self.assertEqual(job.job_file,job_name+'.inp')
        self.assertEqual(job.mp_mode,'threads')
        self.assertEqual(job.local_job_name,job_name)


    def test_job_constructor_invalid(self):
        """
            Test the AbaqusJob constructor using invalid input combinations
        """

        from abaci.AbaqusJob import AbaqusJob
        import exceptions
            
        job_config, job_base_name = self.get_dummy_job()

        # Check constructor fails if both job config and job_file given
        with self.assertRaises(exceptions.ValueError):

            job = AbaqusJob(self.output_dir,job_file=job_base_name+'.inp',
                                job=job_config)

        # Check constructor fails if neither job config or job_file given
        with self.assertRaises(exceptions.ValueError):

            job = AbaqusJob(self.output_dir)
    

    def test_new_job_dir(self):
        """
            Test the finding of a new (non-existent) job directory
        """
        from abaci.AbaqusJob import AbaqusJob
        import os

        job = AbaqusJob(self.output_dir,job_file='myjob')

        # Check sequential job directories are incremental
        for i in range(0,11):

            job_dir = job.get_new_job_dir(self.output_dir)

            expecting = os.path.join(self.output_dir,'myjob_{i}'.format(i=i))
            self.assertEquals(job_dir, expecting)

            os.mkdir(job_dir)


    def test_prepare_job(self):
        """
            Test the AbaqusJob preparation
            Creation of job directory and copying of files
        """

        from abaci.AbaqusJob import AbaqusJob
        import os

        # Create a mock lib directory
        lib_dir = tempfile.mkdtemp()
        open(os.path.join(lib_dir,'usub.f'), 'a').close()

        # Create a mock job file
        fh,job_file = tempfile.mkstemp()
        os.close(fh)
        job_name = os.path.basename(job_file)

        job = AbaqusJob(self.output_dir,job_file=job_file)

        job.prepare_job(lib_dir)

        # Check that job directory has been created
        self.assertTrue(os.path.isdir(job.job_dir))

        # Check that job file has been copied
        self.assertTrue(os.path.exists(os.path.join(job.job_dir,job_name)))

        # Check that job directory contains lib directory
        local_lib_dir = os.path.join(job.job_dir,'lib')
        self.assertTrue(os.path.isdir(local_lib_dir))

        # Check that job local lib dir contains contents of lib dir
        self.assertTrue(os.path.exists(os.path.join(job.job_dir,'lib','usub.f')))

        # Check that env file has been created
        env_file = os.path.join(job.job_dir,'abaqus_v6.env')
        self.assertTrue(os.path.exists(env_file))

        # Check that env file contains reference to job local lib dir
        with open(env_file,'r') as f:

            contents = f.readlines() 

        expecting = 'usub_lib_dir = r"{dir}"'.format(dir=local_lib_dir)
        self.assertIn(expecting,contents[0])


    @unittest.skipUnless(AbaciUnitTestSuite.abaqus_available(),"not running abaqus")
    def test_launch_job(self):
        """
        Test launching of abaqus job
        """
        from abaci.AbaqusJob import AbaqusJob

        # Create a mock lib directory
        lib_dir = tempfile.mkdtemp()

        # Use simple demo job file for testing (no usub needed)
        test_job_file = os.path.join(self.root_dir,'test/data/demo-job.inp')
        job = AbaqusJob(self.output_dir,job_file=test_job_file)

        job.launch_job(nproc=1,lib_dir=lib_dir)

        # Check poll() reports true (is running)
        self.assertTrue(job.poll())

        # Wait for job and check completed successfully
        self.assertTrue(job.wait(verbose=-1) == 0)


    @unittest.skipUnless(AbaciUnitTestSuite.abaqus_available(),"not running abaqus")
    def test_terminate_job(self):
        """
        Test termination of abaqus job
        """
        from abaci.AbaqusJob import AbaqusJob
        import time

        # Create a mock lib directory
        lib_dir = tempfile.mkdtemp()

        # Use simple demo job file for testing (no usub needed)
        test_job_file = os.path.join(self.root_dir,'test/data/demo-job-long.inp')
        job = AbaqusJob(self.output_dir,job_file=test_job_file)

        job.launch_job(nproc=1,lib_dir=lib_dir)

        # Check poll() reports true (is running)
        self.assertTrue(job.poll())

        # Wait for abaqus job to start
        stat_file = os.path.join(job.job_dir,job.local_job_name+'.sta')
        while not os.path.exists(stat_file):
            time.sleep(1)

        # Send termination signal
        job.terminate_job(verbose=-1)
        