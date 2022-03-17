import logging
import os
from os.path import basename, join, splitext, isdir, exists
from utils import cwd, copyfile, system_cmd, system_cmd_wait, copydir, mkdir
from odb_check import compare_odb, dump_ref
from datetime import datetime

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
            self.mp_mode = job['mp-mode']

        else:

            self.name = basename(job_file)
            self.include =[]
            self.job_file = job_file
            self.checks = None
            self.mp_mode = 'threads'

        self.job_dir = self.get_new_job_dir(output_dir)

        self.local_job_file = join(self.job_dir,basename(self.job_file))
        self.local_job_name = splitext(basename(self.local_job_file))[0]
        self.start_time = None
        self.end_time = None
        

    def get_new_job_dir(self,output_dir):
        """Find a new job directory to run job in"""
        stem = join(output_dir,self.name) + "_{counter}"

        counter = 0

        while isdir(stem.format(counter=counter)):

            counter = counter + 1

        return stem.format(counter=counter)


    def launch_job(self,nproc,lib_dir):
        """Launch job"""

        log = logging.getLogger('abaci')

        self.prepare_job(lib_dir)

        abq_cmd = self.get_abaqus_cmd(nproc)
        
        log.info('Launching abaqus for job "%s"',self.name)

        with cwd(self.job_dir):

            self.start_time = datetime.now()

            self.p, self.ofile, self.efile = system_cmd(abq_cmd,output=join(self.job_dir,'abaqus'))


    def is_running(self):
        """
        Check if job is currently running and record end time if not
        (The resolution of recorded end time is how frequently you poll this function)
        """

        log = logging.getLogger('abaci')

        is_running = not isinstance(self.p.poll(),int)

        has_started = self.start_time

        if has_started and (not is_running) and \
            (not self.end_time):

            self.end_time = datetime.now()

            self.duration = self.end_time - self.start_time
            
            log.info('Job "%s" completed. Execution duration: %s', 
                 self.name, self.duration)

        return is_running


    def wait(self,verbose):
        """Wait for the running Abaqus job to finish"""

        log = logging.getLogger('abaci')

        if self.is_running():

            # Job not finished yet
            log.info('Waiting for job "%s" to complete...', self.name)

        stat = system_cmd_wait(self.p,verbose,self.ofile,self.efile)

        return stat


    def terminate_job(self,verbose):
        """Terminate the running Abaqus job"""

        log = logging.getLogger('abaci')

        if not self.is_running():
            
            # Job already completed
            return

        self.p.terminate()

        with cwd(self.job_dir):

            log.info('Cancelling abaqus job "%s"',self.name)

            kill_cmd = ['abaqus', 'terminate','job={name}'.format(name=self.local_job_name)]

            p, ofile, efile = system_cmd(kill_cmd)

            system_cmd_wait(p,verbose)


    def get_abaqus_cmd(self,nproc):
        """Returns the system command to launch abaqus"""

        abq_cmd = ['abaqus','job={name}'.format(name=self.local_job_name)]

        if self.mp_mode != 'disable' and nproc > 1:
            abq_cmd.append('mp_mode={mode}'.format(mode=self.mp_mode))
            abq_cmd.append('cpus={n}'.format(n=nproc))

        abq_cmd.extend(['double','interactive'])

        if os.name == 'nt':
            abq_cmd[0] = 'c:\\SIMULIA\\Commands\\abaqus.bat'
    	    abq_cmd.append('&')
    	    abq_cmd.append('exit')

        return abq_cmd


    def prepare_job(self,lib_dir):
        """Create job directory and copy job files into it"""

        mkdir(self.job_dir)

        copyfile(self.job_file,self.local_job_file)

        for inc in self.include:
            dest = join(self.job_dir,basename(inc))
            copyfile(inc,dest)

        local_lib_dir = join(self.job_dir,'lib')

        copydir(lib_dir,local_lib_dir)

        self.spool_env_file(local_lib_dir)


    def spool_env_file(self,lib_dir):
        """Generate the abaqus_v6.env file"""

        env_file = join(self.job_dir,'abaqus_v6.env')

        with open(env_file,'w') as f:

            f.write('usub_lib_dir = r"{dir}"'.format(dir=lib_dir))


    def __repr__(self):

        return "AbaqusJob({name})".format(name=self.name)


    def run_checks(self):
        """Run reference checks"""
        
        log = logging.getLogger('abaci')

        if not self.checks:
            return

        log.debug('Running regression checks for job "%s"', self.name)

        odb_out_file = join(self.job_dir,self.local_job_name+'.odb')
        odb_ref_file = self.checks['reference']

        if not exists(odb_out_file):
            
            log.warn('Unable to find odb file (%s) for job "%s"',odb_out_file,self.name)

            return

        if not exists(odb_ref_file):

            log.info('Reference file (%s) for job "%s" not found: creating from this run',
                      odb_ref_file, self.name)

            dump_ref(odb_ref_file,odb_out_file,self.name,self.checks)

            return

        compare_odb(odb_ref_file,odb_out_file,self.name,self.checks)