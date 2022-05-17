from abaci.cli import parse_cli, init_logger, init_logger_file
from abaci.config import load_config
from abaci.compile import compile_user_subroutine, collect_cov_report
from abaci.jobs import get_jobs, run_jobs, submit_jobs, post_process
from abaci.utils import mkdir, daemonize
from abaci.dependencies import fetch_dependencies
from abaci.show_info import show_info
from abaci.abaqus import check_for_abaqus

def main():
    """Main entry point for abaci program"""
    
    args = parse_cli()

    init_logger(args.verbose)

    if args.action == 'post':

        post_process(args.job_dir,args.verbose)

        exit()

    config, config_dir = load_config(args.config,False)
         
    dep_list = fetch_dependencies(config, config_dir, args.verbose)

    if args.action == 'show':

        show_info(args, config, dep_list)

        exit()
    
    check_for_abaqus()

    mkdir(config['output'])

    init_logger_file(log_dir=config['output'])

    stat, compile_dir = compile_user_subroutine(args, config['output'], 
                        config['user-sub-file'], config['compile'], dep_list)

    if args.action == 'compile' or stat != 0:
        return

    jobs = get_jobs(args,config)

    if args.action == 'run':

        if args.background:
            daemonize()

        stats = run_jobs(args,compile_dir,jobs)

        for job, stat in zip(jobs,stats):

            if stat == 0:

                job.run_checks()

                job.post_process(args.verbose)

        if args.codecov:
            
            collect_cov_report(config,compile_dir,args.verbose)

    elif args.action == 'submit':

        submit_jobs(compile_dir,jobs,args.interactive,args.no_submit)


if __name__ == "__main__":
    main()