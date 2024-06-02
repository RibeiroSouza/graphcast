from __future__ import annotations

import sys

from graphcast_sdk.src.gcutils.log_config import setup_logging
from graphcast_sdk.src.sdk.remote_cast import cast_from_parameters

setup_logging()

if __name__ == "__main__":
    # the first passed in argument is a filename
    cast_from_parameters(sys.argv[1])
