import logging
from odbAccess import openOdb
import numpy as np
from utils import to_ascii

def check_odb_structure(odb_ref_file,odb_out_file,job_name,checks):
    """Check if the structure of each odb matches that expected by checks config"""

    log = logging.getLogger('abaci')

    odb_out = openOdb(to_ascii(odb_out_file))
    odb_ref = openOdb(to_ascii(odb_ref_file))

    for step in checks['steps']:
            
        step = to_ascii(step)   # Abaqus python doesn't like unicode keys?

        if step not in odb_ref.steps.keys():

            log.fatal('Error while checking job "%s", unable to find step "%s" in reference odb (%s)',
                        job_name, step, odb_ref_file)

            raise Exception('ODB content mismatch')

        if step not in odb_out.steps.keys():

            log.fatal('Error while checking job "%s", unable to find step "%s" in output odb (%s)',
                        job_name, step, odb_out_file)

            raise Exception('ODB content mismatch')

        if checks['frames'] == 'last':

            frames = [len(odb_ref.steps[step].frames)-1]

        elif checks['frames'] == 'all':

            frames = range(0,len(odb_ref.steps[step].frames))

        elif isinstance(checks['frames'],list):

            frames = checks['frames']

        else:

            log.fatal('Error while checking job "%s", unknown frames specified in config: %s',
                job_name, checks['frames'])

            raise Exception('ODB content mismatch')

        if checks['elements'] == 'all':

            field = to_ascii(checks['fields'][0])
            elements = range(0,len(odb_ref.steps[step].frames[0].fieldOutputs[field].values))

        elif isinstance(checks['elements'],list):

            elements = checks['elements']

        else:

            log.fatal('Error while checking job "%s", unknown elements specified in config: %s',
                job_name, checks['frames'])

            raise Exception('ODB content mismatch')

        for i in frames:
            
            if i >= len(odb_ref.steps[step].frames):

                log.fatal('Error while checking job "%s", frame "%s" not found at step %s in reference odb (%s)',
                        job_name, i, step, odb_ref_file)

                raise Exception('ODB content mismatch')

            if i >= len(odb_out.steps[step].frames):

                log.fatal('Error while checking job "%s", frame "%s" not found at step %s in output odb (%s)',
                        job_name, i, step, odb_out_file)

                raise Exception('ODB content mismatch')

            for field in checks['fields']:

                field = to_ascii(field)

                if field not in odb_ref.steps[step].frames[i].fieldOutputs.keys():

                    log.fatal('Error while checking job "%s", field "%s" not found in reference odb (%s)',
                        job_name, field, odb_ref_file)

                    raise Exception('ODB content mismatch')

                if field not in odb_out.steps[step].frames[i].fieldOutputs.keys():

                    log.fatal('Error while checking job "%s", field "%s" not found in reference odb (%s)',
                        job_name, field, odb_ref_file)

                    raise Exception('ODB content mismatch')

    return frames, elements



def compare_odb(odb_ref_file,odb_out_file,job_name,checks):
    """Run comparison checks on two odb files"""
    
    log = logging.getLogger('abaci')

    odb_out = openOdb(to_ascii(odb_out_file))
    odb_ref = openOdb(to_ascii(odb_ref_file))

    frames, elements = check_odb_structure(odb_ref_file,odb_out_file,job_name,checks)

    for step in checks['steps']:
            
        step = to_ascii(step)   # Abaqus python doesn't like unicode keys?

        for i in frames:

            frame_delta = 0

            for field in checks['fields']:

                field = to_ascii(field)

                ref_data = np.array([v.data for ii, v in enumerate(odb_ref.steps[step].frames[i].fieldOutputs[field].values)
                                      if ii in elements])
                out_data = np.array([v.data for ii, v in enumerate(odb_out.steps[step].frames[i].fieldOutputs[field].values)
                                      if ii in elements])

                field_rms = np.sqrt( np.square(ref_data - out_data).mean() )
                
                log.debug('Job "%s", Step "%s", Frame %s, Field %s, RMS Delta = %s',
                        job_name, step, i, field, field_rms)

                frame_delta = frame_delta + np.square(field_rms)

            frame_rms = np.sqrt( frame_delta.mean() )

            log.info('Job "%s", Step "%s", Frame %s, RMS Delta = %s',
                        job_name, step, i, frame_delta)
