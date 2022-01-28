import sys
import logging
from odbAccess import openOdb
import numpy as np
# from abaci.utils import to_ascii

def compare_fields(odb_ref,odb_out,step,frame,field):

    ref_data = np.array([v.data for v in odb_ref.steps[step].frames[frame].fieldOutputs[field].values])
    out_data = np.array([v.data for v in odb_out.steps[step].frames[frame].fieldOutputs[field].values])

    rms_diff = np.sqrt( np.square(ref_data - out_data).mean() )

    return rms_diff


def compare_frames(odb_ref,odb_out,step,frame):

    # Check fields
    for field in odb_ref.steps[step].frames[frame].fieldOutputs.keys():

        if field not in odb_out.steps[step].frames[frame].fieldOutputs.keys():

            print 'Step "{step}", Frame {frame}, field {field} from $1 not found in $2'.format(
                step = step, frame=frame, field=field)

            continue

    n = 0
    rms_diff = 0
    for field in odb_out.steps[step].frames[frame].fieldOutputs.keys():

        if field not in odb_ref.steps[step].frames[frame].fieldOutputs.keys():

            print 'Step "{step}", Frame {frame}, field {field} from $1 not found in $2'.format(
                step = step, frame=frame, field=field)

            continue

        n = n + 1
        rms_diff = rms_diff + np.square(compare_fields(odb_ref,odb_out,step,frame,field))

    rms_diff = np.sqrt( rms_diff/n )
    
    print 'Step "{step}", Frame {frame}, rms diff = {diff}'.format(
                step = step, frame=frame, diff=rms_diff)


def compare_steps(odb_ref,odb_out,step):

    # Check frames
    nref = len(odb_ref.steps[step].frames)
    nout = len(odb_out.steps[step].frames)

    if nref == nout:

        print 'Step "{step}": number of frames ({n}) matches'.format(
               step=step, n=nref)

        frames = range(0,nref-1)

    else:

        print 'Step "{step}": frame number mismatch'.format(step=step)
        print '               n1 = {n}'.format(n=nref)
        print '               n2 = {n}'.format(n=nout)
        
        if min(nref,nout) > 0:
            print '   (Comparing last frame only)'

            frames = [-1]

        else:
            print 'Step "{step}": skipping frame comparison'.format(step=step)
            return

    for frame in frames:

        compare_frames(odb_ref,odb_out,step,frame)

def main():

    if len(sys.argv) < 2:
        raise Exception("Not enough arguments, please specify two odb files.")

    ref_file = sys.argv[1]
    out_file = sys.argv[2]

    odb_ref = openOdb(ref_file)
    odb_out = openOdb(out_file)

    # Check steps match
    for step in odb_ref.steps.keys():

        if step not in odb_out.steps.keys():

            print 'Step "{step}" from $1 not found in $2'.format(step = step)

            continue
            
    for step in odb_out.steps.keys():

        if step not in odb_ref.steps.keys():

            print 'Step "{step}" from $1 not found in $2'.format(step = step)

            continue

        compare_steps(odb_ref,odb_out,step)



if __name__ == "__main__":
    main()