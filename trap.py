# A script that can "trap" any file or dir with a pin.
#
# Author: Indrajit Ghosh
#
# Created on: Mar 22, 2023
#

import string, time, shutil, sys, argparse
from distutils.dir_util import copy_tree
from itertools import product
from pathlib import Path, PurePath

UPPERCASE = list(string.ascii_uppercase)
DIGITS = list(string.digits)

def _create_path_from_str(dir:Path=Path.cwd(), s:str="ABC"):
    """
    Returns:
    --------
        "A/B/C"
    """
    return Path(PurePath(dir, '/'.join(s)))

def _get_list_of_paths(keywords:list=None, dir:Path=Path.cwd()):
    
    if keywords is None:
        keywords = ["AA", "AB", "BA", "BB"]

    return [_create_path_from_str(dir=dir, s=k) for k in keywords]


def _create_directory_trap(target:Path, depth:int=2, symbols:list=["A", "B", "C"]):
    """
    This function will create directories with all possible strings that 
    can be made from `symbols` of length `depth` inside the dir `target`.

    Parameters:
    -----------
        `target`: `Path`; Path of the dir where the trap is to be created
        `depth`: `int`; A integer indicating the level of the trap
        `symbols`: `list`: symbols to be used

    Example:
    ---------
        Suppose target = Path.cwd() / "trash"
        >>> _create_directory_trap(target, depth = 2, symbols = ["A", "B"])

        This will create all dirs "A/A", "A/B", "B/A" and "B/B" inside `target`
    """

    keywds = [''.join(c) for c in product(symbols, repeat = depth)]

    N = len(symbols)
    
    paths = _get_list_of_paths(keywords=keywds, dir=target)

    for p in paths:
        print(f" - Creating {p}")
        p.mkdir(parents=True, exist_ok=True)

    print(f" - Total paths created {len(keywds)}")


def trap(item:Path=None, pin:str="0123"):
    """
    Traps the `item`.
    If the `item` is a file then this function copy the file into trapped/pin
    if the `item` is a directory then it copies the whole directory into trapped/pin
    """
    pin = str(pin)
    trap_dir = Path.cwd() / "trapped"
    _create_directory_trap(target=trap_dir, depth=len(pin), symbols=DIGITS)

    if item is not None:

        item = Path(item).absolute()

        trap_loc = _create_path_from_str(dir=trap_dir, s=pin)
        if item.is_file():
            shutil.copy(src=item, dst=trap_loc)
        else:
            dst_dir = trap_loc / item.name
            if not dst_dir.exists():
                dst_dir.mkdir()
            copy_tree(src=str(item), dst=str(dst_dir))

        print(f"\n The item has been trapped inside the dir\n {trap_dir}\nwith the pin {pin}.\n")
    else:
        print(f"\n A `trapped` directory has been created of depth {len(pin)}!\n")

    

def main():
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="Description of your script")

    # Add the -f or --file option with a default value of None
    parser.add_argument('-f', '--file', help='Path to the item file', default=None)

    # Add the -p or --pin option
    parser.add_argument('-p', '--pin', help='PIN')

    # Parse the command-line arguments
    args = parser.parse_args()

    # Check if the -p option is provided
    if not args.pin:
        print("Usage: python script.py -p <pin>")
        sys.exit(1)

    item_path = Path(args.file) if args.file else None
    my_pin = args.pin

    t1 = time.time()
    # Call your trap function here with item_path and my_pin
    trap(item=item_path, pin=my_pin)
    t2 = time.time()

    print(f"\n Total time taken: {t2 - t1} secs.\n")

if __name__ == '__main__':
    main()
