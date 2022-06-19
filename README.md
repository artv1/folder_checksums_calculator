# Folder checksums calculator
The program calculates SHA-1/256/512 checksums for all files in a specified folder, as well as its subfolders.

Among the features of the program:
* calculating checksums for all files in a folder and creating a database for them
* checking all files from the database for integrity
* finding changes in the working folder and the ability to update data in the database
* calculation, storage and verification of checksums for a single file

To use this console utility, you must have Python installed on your computer. If it's done, type in terminal:

    python fcc.py
---
Argument can be used to specify the path to the folder with files. For example:

    python fcc.py /home/user/folder-to-work

To verify the files in a folder, simply use the previously created database file as the path

    python fcc.py shadata_... .json

---
Two versions of the program are presented.

### fcc.py
Recommended for most users. It uses JSON as a database and handles data changes more flexibly.

---
### folder_checksums_calculator.py
Stores data in a simple text file. This option is a little outdated, but is suitable for those who need to use plain text data.
