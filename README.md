# GAO Fund Newsletter/Factsheet Monthly Return Database

This program automatically scrapes the monthly return from factsheets and stores them in CSV spreadsheets for ease of viewing. 

# Getting Started
## Installation
### Mac OS
Open a new terminal and run
```
git clone https://github.com/avbdasf/fund-database-tool.git
``` 

### Windows
Install Python 3.9 from [this link](https://www.python.org/downloads/release/python-3919/).

Then install Winget from [this link](https://github.com/microsoft/winget-cli/releases/download/v1.8.1911/Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle). 

Then open a Command Prompt and copy and paste the following, then press enter
```
winget install --id GitHub.cli
```

Then in the same Command Prompt, run
```
gh repo clone https://github.com/simnlee/fund-database-tool
```

Install pip by running 
```
python -m ensurepip
```

Move to this project's directory by running the below command.
```
cd fund-database-tool
```

Install project dependencies by running
```
python3 -m pip install -r requirements.txt
```

## Folder Structure 
All PDFs are kept in the "data/" folder. The folder should always be structured as follows: 
```
data
├── 2024
│   ├── June
│   │   ├── examplefund1.pdf
│   │   └── examplefund1.pdf
│   │   └── ...
│   ├── July
│   │   ├── examplefund1.pdf
│   │   └── examplefund1.pdf
│   │   └── ...
```

Make sure the names of the month folders are always capitalized. 

## Usage Instructions 
### Creating the CSV spreadsheet
Ensure that you are first in the project directory. To get the monthly returns of all funds in the folder "data/YEAR/MONTH" then run 
```
python3 -m main.py --folderPath data/YEAR/MONTH
```

For instance, if you want to get the monthly returns of all factsheets stored in the folder "data/2024/June/" then run 
```
python3 -m main.py --folderPath data/2024/June
```

After the command is done running, there will be a new CSV spreadsheet file in the month folder named "YEAR_MONTH.csv" which is structured as follows: 
|   Filename    |   Monthly Return  |
|   --------    |   ------- |
| examplefund1.pdf |  1.03% |
| examplefund2.pdf | -2.34% |
| examplefund3.pdf |  4.95% |

### Updating the spreadsheet with new factsheets/newsletters
After the CSV file is created, you can update it when new factsheets/newsletters are received. Put the new PDF(s) in the corresponding "data/YEAR/MONTH" folder and run 
```
python3 -m main.py --folderPath data/YEAR/MONTH
```

The monthly returns from any new file(s) added to the month folder will be appended to the spreadsheet. 
