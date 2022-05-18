# folder_checksums_calculator
The program calculates SHA1 checksums for all files in a given folder, as well as its subfolders. A list of all files and their checksums is saved and can be used to check the integrity of the data.

To use this console utility, you must have Python installed on your computer. If it's done, type in terminal:

    python folder_checksums_calculator.py
---
Argument can be used to specify the path to the folder with files. For example:

    python folder_checksums_calculator.py /home/user/folder-to-work

To verify the files in a folder, simply use the previously created database file 'checksums_list_for... .txt' as the path

    python folder_checksums_calculator.py checksums_list_for... .txt

If you just run the program without any argument by: "python folder_checksums_calculator.py"
the program will prompt you to enter the path to the folder for which you want to calculate sha1 for all files. In this field, you can also specify the path to the 'database' (list-file) to check the integrity of the files contained in it.

---
In short, it is possible to use both a command line argument and input inside a script to specify a path
