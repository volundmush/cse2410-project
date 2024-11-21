# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from mconverter.dataimporter import DataImporter
from pathlib import Path


def main():
    p = Path("nmi.tif")
    importer = DataImporter(p)
    data = importer.process()
    print(data)
    return data



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
