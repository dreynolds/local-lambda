#!/usr/bin/env python
import sys
from pathlib import Path

from lambda_server import main

sys.path.insert(0, Path.cwd().as_posix())
main()
