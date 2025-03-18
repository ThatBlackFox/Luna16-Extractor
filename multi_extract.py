# lets take only 2 subsets at a time for now
from utils import cli_multi_extractor_handler, cli_make_handler
from concurrent.futures import ThreadPoolExecutor
import sys


def main():
    args = sys.argv
    batch_args = cli_multi_extractor_handler.main(args)
    with ThreadPoolExecutor(max_workers=len(batch_args)//2) as executor:
        executor.map(cli_make_handler.extracting, batch_args)

if __name__ == "__main__":
    main()
