import argparse
import sys
import json
from pathlib import Path

from utils import get_function_from_string

sys.path.insert(0, Path.cwd().as_posix())

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", type=str, nargs=1, help="The command to call")
    parser.add_argument(
        "--event",
        type=str,
        action="store",
        help="The event to pass to the command",
        default="{}",
    )
    parser.add_argument(
        "--context",
        type=str,
        action="store",
        help="The event to pass to the command",
        default="{}",
    )
    args = parser.parse_args()

    func = get_function_from_string(args.command[0])
    if func:
        try:
            event = json.loads(args.event)
        except json.JSONDecodeError:
            event = {}
        try:
            context = json.loads(args.context)
        except json.JSONDecodeError:
            context = {}
        output = func(event, context)
        print(json.dumps(output))
