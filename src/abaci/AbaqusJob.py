import logging
import os
from os.path import basename, join, splitext, isdir, exists
from utils import cwd, copyfile, system_cmd, system_cmd_wait, copydir, mkdir, relpathshort, prompt_input_default
import abaci.abaqus as abq
from abaci.config import get_default_cluster_schema
from datetime import datetime
from exceptions import ValueError
import cPickle as pkl
import abaci.slurm as slurm

class AbaqusJob:

    def __init__(self,output_dir,job=None,job_file=None):
        """Constructor"""

        if bool(job) is bool(job_file):

            raise ValueError('AbaqusJob needs one of job or job_file to instantiate')

        if job:

            self.job_file = job['job-file']
            self.include = job['include']

            if job['name']:
                self.name = job['name']
            else:
                self.name = splitext(basename(self.job_file))[0]
            
            self.checks = job['check']
            self.postprocess = job['post-process']
            self.mp_mode = job['mp-mode']
            self.cluster = job['cluster']

        else:

            cluster_schema, cluster_defaults = get_default_cluster_schema()

            self.name = basename(job_file)
            self.include =[]
            self.job_file = job_file
            self.checks = None
            self.postprocess = None
            self.mp_mode = 'threads'
            self.cluster = cluster_defaults

        self.job_dir = self.get_new_job_dir(output_dir)

        self.local_job_file = join(self.job_dir,basename(self.job_file))
        self.cache_file = join(self.job_dir,'abaci-cache.pkl')
        self.local_job_name = splitext(basename(self.local_job_file))[0]
        self.start_time = None
        self.end_time = None
        self.job_script = None
        

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
        
        log.info('Launching abaqus for job "%s"',self.name)

        self.start_time = datetime.now()

        self.p, self.ofile, self.efile = abq.run(dir=self.job_dir,
                                          job_name=self.local_job_name,
                                          mp_mode=self.mp_mode,
                                          nproc=nproc)


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

        log.info('Cancelling abaqus job "%s"',self.name)

        p, ofile, efile = abq.terminate(dir=self.job_dir,job_name=self.local_job_name)

        if os.name != 'nt':
                
            system_cmd_wait(p,verbose)


    def cluster_config_interactive_override(self):
        """Interactively let user override default cluster settings"""

        self.mp_mode = prompt_input_default('  mp_mode: ', self.mp_mode)

        for field in self.cluster:

            if self.mp_mode == 'threads':

                if field == 'tasks-per-node' or field == 'nodes':

                    continue

            elif self.mp_mode == 'mpi':

                if field == 'cpus-per-task':

                    continue

            elif self.mp_mode == 'disable':

                if field == 'tasks-per-node' or field == 'nodes' or field == 'cpus-per-task':

                    continue

            else:

                raise Exception('AbaqusJob: invalid mp_mode specified interactively.')

            self.cluster[field] = prompt_input_default('  {f}: '.format(f=field),
                                                        self.cluster[field])


    def submit_job(self):
        """Submit job to cluster"""

        log = logging.getLogger('abaci')
        
        log.info('Submitting abaqus job "%s" via slurm',self.name)
        
        job_id = slurm.submit_job(self.job_dir,self.job_script,'')

        log.info('Job id is "%s"',job_id)


    def spool_job_script(self,env_modules):
        """Generate a cluster job script in job dir"""

        self.job_script = join(self.job_dir,'sljob')

        if self.mp_mode == 'threads':

            self.cluster['tasks-per-node'] = 1
            self.cluster['nodes'] = 1

        elif self.mp_mode == 'mpi':

            self.cluster['cpus-per-task'] = 1

        elif self.mp_mode == 'disable':

            self.cluster['tasks-per-node'] = 1
            self.cluster['nodes'] = 1
            self.cluster['cpus-per-task'] = 1

        nproc = self.cluster['tasks-per-node'] * self.cluster['cpus-per-task'] * self.cluster['nodes']

        if self.mp_mode == 'mpi':

            cmd = abq.get_mpi_job_allocation_cmd()

        else:

            cmd = []


        cmd.append(' '.join(abq.get_run_cmd(self.local_job_name,self.mp_mode,nproc)))

        slurm.spool_job_script(self.job_script,env_modules,cmd,job_name=self.local_job_name,
                               time=self.cluster['time'],
                               nodes=self.cluster['nodes'],
                               partition=self.cluster['partition'],
                               tasks_per_node=self.cluster['tasks-per-node'],
                               cpus_per_task=self.cluster['cpus-per-task'],
                               mem_per_cpu=self.cluster['mem-per-cpu'],
                               email=self.cluster['email']
                               )


    def prepare_job(self,lib_dir):
        """Create job directory and copy job files into it"""

        log = logging.getLogger('abaci')

        log.info('Preparing job "%s" in directory "%s"',self.name,relpathshort(self.job_dir))

        mkdir(self.job_dir)

        copyfile(self.job_file,self.local_job_file)

        for inc in self.include:
            dest = join(self.job_dir,basename(inc))
            copyfile(inc,dest)

        local_lib_dir = join(self.job_dir,'lib')

        copydir(lib_dir,local_lib_dir)

        self.spool_env_file(local_lib_dir)

        # Cache full job info to file for post-processing subcommand
        with open(self.cache_file,'w') as f:
            pkl.dump(self,f)


    def spool_env_file(self,lib_dir):
        """Generate the abaqus_v6.env file"""

        env_file = join(self.job_dir,'abaqus_v6.env')

        with open(env_file,'w') as f:

            f.write('usub_lib_dir = r"{dir}"'.format(dir=lib_dir))


    def __repr__(self):

        return "AbaqusJob({name})".format(name=self.name)


    def run_checks(self):
        """Run reference checks"""
        
        from odb_check import compare_odb, dump_ref

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


    def post_process(self,verbosity):
        """Run any post-processing scripts for this job"""

        if not self.postprocess:

            return

        log = logging.getLogger('abaci')

        abq_py = ' '.join(abq.abaqus_cmd(['python'],noshell=True))
        post_cmd = self.postprocess.format(
            PY=abq_py,
            JOB=self.local_job_name,
            ODB=join(self.job_dir,self.local_job_name+'.odb'),
            DIR=self.job_dir
        )

        log.info('Running post-processing script for job "%s"', self.name)

        p, ofile, efile = system_cmd(post_cmd.split())

        stat = system_cmd_wait(p, verbosity, ofile, efile)

        if stat != 0:

            log.warn('Post-processing script exited with non-zero status')

        return stat