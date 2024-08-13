from database import *
from data_processing import *
import argparse
import os

def main():
    # Argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--folderPath", help="Path to the folder containing the PDF files for one month")
    args = parser.parse_args()
    cwd = os.getcwd()

    process_folder(os.path.join(cwd, args.folderPath))

if __name__ == "__main__":
    main()