import argparse
import sys
from pathlib import Path
from utils import load_interface


def main(src_file, dst_file, ask_override):
    if not load_interface(src_file, dst_file, ask_override):
        print("File was NOT copied!!")
        return False
    return True


if __name__ == "__main__":
    # create the top-level parser
    parser = argparse.ArgumentParser(prog='HARMONY CLI')
    parser.add_argument("source_file", type=str, help="source file to copy.")
    parser.add_argument("destiny_file", type=str, help="destiny of file to copy.")
    parser.add_argument("-ask_override", "-ask", action=argparse.BooleanOptionalAction,
                        help="Flag to ask if want to override destiny file.")

    # parse arguments
    args = parser.parse_args()
    src = Path(args.source_file)
    dst = Path(args.destiny_file)
    ask = args.ask_override

    main(src, dst, ask)

    sys.exit("EOF!")
