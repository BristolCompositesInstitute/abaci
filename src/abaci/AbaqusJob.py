import logging
from os import mkdir
from os.path import basename, join, splitext, isdir
from utils import cwd, copyfile, system_cmd

class AbaqusJob:

    def __init__(self,output_dir,job=None,job_file=None):
        """Constructor"""

        if bool(job) is bool(job_file):

            raise Exception('AbaqusJob needs one of job or job_file to instantiate')

        if job:

            self.job_file = job['job-file']
            self.include = job['include']

            if job['name']:
                self.name = job['name']
            else:
                self.name = splitext(basename(job_file))[0]
            
            self.checks = job['check']

        else:

            self.name = basename(job_file)
            self.include =[]
            self.job_file = job_file
            self.checks = None

        self.job_dir = self.get_new_job_dir(output_dir)

        
    def get_new_job_dir(self,output_dir):
        """Find a new job directory to run job in"""
        stem = join(output_dir,self.name) + "_{counter}"

        counter = 0

        while isdir(stem.format(counter=counter)):

            counter = counter + 1

        return stem.format(counter=counter)


    def run_job(self,lib_dir,verbosity):
        """Launch job"""

        import os

        log = logging.getLogger('abaci')

        mkdir(self.job_dir)

        local_job_file = join(self.job_dir,basename(self.job_file))

        copyfile(self.job_file,local_job_file)

        for inc in self.include:
            dest = join(self.job_dir,basename(inc))
            copyfile(inc,dest)

        job_name = splitext(basename(local_job_file))[0]

        self.spool_env_file(lib_dir)

        abq_cmd = ['abaqus','job={name}'.format(name=job_name),
                       'double','interactive']

        if os.name == 'nt':
            abq_cmd[0] = 'c:\\SIMULIA\\Commands\\abaqus.bat'
        
        log.info('Running abaqus')

        with cwd(self.job_dir):

            system_cmd(abq_cmd,verbosity)


    def spool_env_file(self,lib_dir):
        """Generate the abaqus_v6.env file"""

        env_file = join(self.job_dir,'abaqus_v6.env')

        with open(env_file,'w') as f:

            f.write('usub_lib_dir = "{dir}"'.format(dir=lib_dir))


    def __repr__(self):

        return "AbaqusJob({name}:{file}".format(name=self.name,file=self.job_file)


    def run_checks(self):
        """Run reference checks"""
        pass
