# lets take only 2 subsets at a time for now
from utils import cli_multi_patch_handler, cli_patch_handler
from concurrent.futures import ThreadPoolExecutor
import sys


def main():
    args = sys.argv
    batch_args = cli_multi_patch_handler.main(args)
    with ThreadPoolExecutor(max_workers=len(batch_args)//2) as executor:
        executor.map(cli_patch_handler.patching, batch_args)

if __name__ == "__main__":
    main()
