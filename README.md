# Folder checksums calculator
The program calculates SHA-1/256/512 checksums for all files in a specified folder, as well as its subfolders. A list of files with their checksums is stored and can be used to check the data integrity.

To use this console utility, you must have Python installed on your computer. If it's done, type in terminal:

    python folder_checksums_calculator.py
---
Argument can be used to specify the path to the folder with files. For example:

    python folder_checksums_calculator.py /home/user/folder-to-work

To verify the files in a folder, simply use the previously created database file 'checksums_list_for... .txt' as the path

    python folder_checksums_calculator.py checksums_list_for... .txt

If you just run the program without any argument by: "python folder_checksums_calculator.py"
the program will prompt you to enter the path to the folder where you want to calculate checksums for all files. In this field, you can also specify the path to the 'database' to check the integrity of the files listed in it.

---
A simple text file containing a list of files and their checksums is used as a database. This text file can also be opened and used from outside of this application.
