from database import *
from data_processing import *
import argparse

def main():
    """
    # Argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--folderPath", help="Path to the folder containing the PDF files for one month")
    args = parser.parse_args()
    """

    process_folder("data/factsheets/2024/June")
    #process_folder_json("factsheets/json/2024/April")
    #print(get_return_from_pdf("data/factsheets/2024/June/Akahi Fund LP June 2024 Newsletter.pdf"))

if __name__ == "__main__":
    main()