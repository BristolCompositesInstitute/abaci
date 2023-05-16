import sys
from abaci.cli import parse_cli, init_logger, init_logger_file
from abaci.config import load_config, init_new_config
from abaci.compile import compile_user_subroutine, collect_cov_report
from abaci.jobs import get_jobs, run_jobs, submit_jobs, post_process
from abaci.utils import mkdir, daemonize
from abaci.dependencies import fetch_dependencies
from abaci.show_info import show_info
from abaci.abaqus import check_for_abaqus
from abaci.tests import discover_tests, gen_test_driver, compile_tests, run_tests

def main():
    """Main entry point for abaci program"""
    
    args = parse_cli()

    init_logger(args.verbose)

    if args.action == 'post':

        post_process(args.job_dir,args.verbose)

        exit()

    elif args.action == 'init':

        init_new_config(args.config,user_sub_file=args.config_usub_file,
                                    output=args.config_output_path,
                                    full=args.full_config,
                                    bare=args.bare_config,
                                    overwrite=args.overwrite_config)
        exit()

    config, config_dir = load_config(args.config,args.action,False)
         
    dep_list = fetch_dependencies(config, config_dir, args.verbose)

    if args.action == 'show':

        show_info(args, config, dep_list)

        exit()
    
    check_for_abaqus()

    mkdir(config['output'])

    init_logger_file(log_dir=config['output'])

    stat, compile_dir, fflags = compile_user_subroutine(args, config['output'], 
                        config['user-sub-file'], config['compile'], dep_list)

    if args.action == 'compile' or stat != 0:
        return

    elif args.action == 'test':

        test_sources, testsuites = discover_tests(config['test-mod-dir'])
        
        if not testsuites:

            sys.exit(1)
            
        test_driver_file = gen_test_driver(testsuites, compile_dir)

        test_driver = compile_tests(args, config['user-sub-file'], fflags, compile_dir, test_driver_file, test_sources)

        stat = run_tests(test_driver, compile_dir, args.verbose)

        if args.codecov:
            
            collect_cov_report(config,compile_dir,args.verbose)
            
        sys.exit(stat)

    jobs = get_jobs(args,config)

    if args.action == 'run':

        if args.background:
            daemonize()

        stats = run_jobs(args,compile_dir,jobs)

        exitstat = 0

        for job, stat in zip(jobs,stats):

            if stat == 0:

                job.run_checks()

                job.post_process(args.verbose)

            else:

                exitstat = 1

        if args.codecov:
            
            collect_cov_report(config,compile_dir,args.verbose)

        exit(exitstat)
        
    elif args.action == 'submit':

        submit_jobs(compile_dir,jobs,args.interactive,args.no_submit)


if __name__ == "__main__":
    main()