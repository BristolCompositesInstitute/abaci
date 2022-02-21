import logging
from os import mkdir
from os.path import basename, join, splitext, isdir, exists
from utils import cwd, copyfile, system_cmd
from odb_check import compare_odb, dump_ref

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
        
    def get_new_job_dir(self,output_dir):
        """Find a new job directory to run job in"""
        stem = join(output_dir,self.name) + "_{counter}"

        counter = 0

        while isdir(stem.format(counter=counter)):

            counter = counter + 1

        return stem.format(counter=counter)


    def run_job(self,args,lib_dir):
        """Launch job"""

        import os

        log = logging.getLogger('abaci')

        mkdir(self.job_dir)

        copyfile(self.job_file,self.local_job_file)

        for inc in self.include:
            dest = join(self.job_dir,basename(inc))
            copyfile(inc,dest)

        self.spool_env_file(lib_dir)

        abq_cmd = ['abaqus','job={name}'.format(name=self.local_job_name)]

        if args.nproc > 1:
            abq_cmd.append('mp_mode={mode}'.format(mode=self.mp_mode))
            abq_cmd.append('cpus={n}'.format(n=args.nproc))

        abq_cmd.extend(['double','interactive'])

        if os.name == 'nt':
            abq_cmd[0] = 'c:\\SIMULIA\\Commands\\abaqus.bat'
        
        log.info('Running abaqus for job "%s"',self.name)

        with cwd(self.job_dir):

            try:
                stat = system_cmd(abq_cmd,args.verbose,output=join(self.job_dir,'abaqus'))

            except:

                log.info('Cancelling abaqus job "%s"',self.name)

                kill_cmd = [abq_cmd[0], 'terminate','job={name}'.format(name=self.local_job_name)]

                system_cmd(kill_cmd,args.verbose)

                stat = -1

        return stat


    def spool_env_file(self,lib_dir):
        """Generate the abaqus_v6.env file"""

        env_file = join(self.job_dir,'abaqus_v6.env')

        with open(env_file,'w') as f:

            f.write('usub_lib_dir = r"{dir}"'.format(dir=lib_dir))


    def __repr__(self):

        return "AbaqusJob({name}:{file}".format(name=self.name,file=self.job_file)


    def run_checks(self):
        """Run reference checks"""
        
        log = logging.getLogger('abaci')

        if not self.checks:
            return

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