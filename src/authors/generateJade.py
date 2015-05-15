import sys
from authorsTool import *

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print """Usage: {0} <userid>
Generate a jade file for the basic information of the given zhihu user id, and print it to stdout
Example: python {0} grapeot
""".format(sys.argv[0])
        sys.exit(-1)

    xs, ys = generateHoursFigure(sys.argv[1])
    sys.stdout.write('.')
