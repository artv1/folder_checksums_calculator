# folder_checksums_calculator
The program calculates SHA1 checksums for all files in a given folder, as well as its subfolders. A list of all files and their checksums is saved and can be used to check the integrity of the data.

To use this console utility, you must have Python installed on your PC.
Type in terminal: python folder_checksums_calculator.py
You also can use arguments to specify path to folder or previous calculated database file. For example:

python folder_checksums_calculator.py /home/user/folder-to-work

To verify files in folder just use as path previous created database file 'checksums_list_for... .txt'

If you just run the program without arguments by: "python folder_checksums_calculator.py"
the program will prompt you to enter the path to the folder for which you want to calculate sha1 for all files. In this field, you can also specify the path to the list file to check the integrity of the files contained in it.

In short, it is possible to use both a command line argument and input inside a script to specify a path
