from redist import toml
import os
from abaci.cli import parse_cli, init_logger, init_logger_file
from abaci.config import load_config, list_config_jobs
from abaci.compile import compile_user_subroutine, collect_cov_report
from abaci.jobs import get_jobs, run_jobs
from abaci.utils import mkdir, daemonize
from abaci.dependencies import fetch_dependencies

def main():
    """Main entry point for abaci program"""

    args = parse_cli()

    init_logger(args.verbose)

    config, config_dir = load_config(args.config,False)
         
    dep_list = fetch_dependencies(config, config_dir, args.verbose)

    if args.action == 'show':
         
        if 'config' in args.object:

            print(toml.dumps(config))

        if 'jobs' in args.object:

            list_config_jobs(config,args.verbose)

        if 'dependencies' in args.object:

            for dep_name,dep in dep_list.items():
                    
                    print('  {name} {ver} {git}'.format(name=dep_name,
                                                         ver=dep['version'],git=dep['git']))
            
        if 'sources' in args.object:

            sources = [config['user-sub-file']] + config['compile']['include']

            for dep_name,dep in dep_list.items():

                sources.extend(dep['includes'])

            for file in sources:

                print(os.path.relpath(file))

        exit()

    mkdir(config['output'])

    init_logger_file(log_dir=config['output'])

    stat, compile_dir = compile_user_subroutine(args, config['output'], 
                        config['user-sub-file'], config['compile'], dep_list)

    if args.action == 'compile' or stat != 0:
        return

    jobs = get_jobs(args,config)

    if args.background:
        daemonize()

    stats = run_jobs(args,compile_dir,jobs)

    for job, stat in zip(jobs,stats):

        if stat == 0:

            job.run_checks()

    if args.codecov or config['compile']['code-coverage']:
        
        collect_cov_report(config,compile_dir,args.verbose)


if __name__ == "__main__":
    main()