import sys

from gcutils.log_config import setup_logging

from .remote_cast import cast_from_parameters

setup_logging()

if __name__ == "__main__":
    # the first passed in argument is a filename
    cast_from_parameters(sys.argv[1])
