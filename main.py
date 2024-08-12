from database import *
from data_processing import *
import argparse

def main():
    # Argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--folderPath", help="Path to the folder containing the PDF files for one month")
    args = parser.parse_args()

    process_folder(args.folderPath)
    #process_folder_json(args.folderPath)

if __name__ == "__main__":
    main()