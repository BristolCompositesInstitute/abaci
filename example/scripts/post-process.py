import sys
from odbAccess import openOdb
import numpy as np

def main():
    """
        Example post-processing script for Abaqus

        COMMAND LINE ARGUMENTS:
          [1] path to the Abaqus output database (.odb)
          [2] path to output directory

    """

    odb_file = sys.argv[1]
    output_dir = sys.argv[2]

    print '  ODB file "{f}"'.format(f=odb_file)
    print '  Output directory: "{d}"'.format(d=output_dir)

    odb = openOdb(odb_file,readOnly=True)

    # Iterate over job steps
    for step in odb.steps.keys():

        print '  '+step

        # Iterate over saved frames
        for frame in odb.steps[step].frames:

            displacement = np.array([v.data for v in frame.fieldOutputs['U'].values])

            max_dis = np.max(displacement)

            print '    frame {f}, time {t}, max displacement = {d}'.format(
                f = frame.frameId,
                t = frame.frameValue,
                d = max_dis
            )


if __name__ == '__main__':
    main()
