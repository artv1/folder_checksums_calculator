# https://github.com/artv1/folder_checksums_calculator

import os, hashlib, sys
from datetime import datetime

# sha1 calculating
def sha1_calc(filename):
    with open(filename, "rb") as f:
        hash = hashlib.sha1()
        while chunk := f.read(65536):
            hash.update(chunk)
    return hash.hexdigest()

# sha256 calculating
def sha256_calc(filename):
    with open(filename, "rb") as f:
        hash = hashlib.sha256()
        while chunk := f.read(65536):
            hash.update(chunk)
    return hash.hexdigest()

# sha512 calculating
def sha512_calc(filename):
    with open(filename, "rb") as f:
        hash = hashlib.sha512()
        while chunk := f.read(65536):
            hash.update(chunk)
    return hash.hexdigest()

# converting bytes to readable form
def converting_bytes(bytes):
    converted = bytes
    if converted > 1024:
        converted /= 1024
        xB = 'KiB'
        if converted > 1024:
            converted /= 1024
            xB = 'MiB'
            if converted > 1024:
                converted /= 1024
                xB = 'GiB'
                if converted > 1024:
                    converted /= 1024
                    xB = 'TiB'
    else:
        return f"{bytes} bytes"

    return f"{str(round(converted,1))} {xB} ({'{:,}'.format(bytes)} bytes)"

#terminal argument input
if len(sys.argv) > 1:
    # if argument contains spaces, use all arguments to build path
    joint_path = " ".join(sys.argv[1:])

    # if the argument is a path to a folder or file, use it
    if os.path.isdir(joint_path) or os.path.isfile (joint_path):
        dir = joint_path

    else:
        print (f"Path '{joint_path}' not found. Enter the path to the folder or file")
        exit()

else:
    # if no argument detected
    dir = input("Enter path: ") #getting the path to the working folder

dir = os.path.abspath(dir)

'''
Check if the specified [dir] is the path to the database file.
If so, then the program works in the mode of checking existing files for compliance with the database.
If not, the program skips this module and works in the mode of calculating checksums in the specified folder
'''

if os.path.isfile (dir) and os.path.basename(dir).startswith("checksums_list_for_"):
    print (f"{50*'-'}\nYou've selected a DATABASE file: {os.path.basename(dir)}\nLet's begin verification\n{50*'-'}\n")

    # now 'dir' is path to database file, so open it
    dfile = open(dir, encoding="utf-8")

    # path to the folder where the database file [dir] is located
    check_dir = os.path.join(os.path.dirname(dir),'')

    d_content = dfile.readlines()
    raw_data = d_content[4:]

    new_list = [s.replace("\n", "") for s in raw_data]
    clear_list = list(filter(None, new_list)) # list of files and hashsums only

    good_files = list() # files that have been verified against database
    bad_files = list() # files that have NOT been verified against database

    for cheking_file in clear_list:
        if os.path.isfile(check_dir + cheking_file):
            
            old_sha = clear_list[clear_list.index(cheking_file)+1] # next element is old sha1 from database
            
            if len(old_sha) == 40:
                # the database stores SHA-1 checksums
                ch_sum = sha1_calc(check_dir + cheking_file)

                print(f"Calculating SHA-1 for {int(clear_list.index(cheking_file)/2+1)} of {int(len(clear_list)/2)} files in the list")

                if old_sha == ch_sum:
                    good_files += [cheking_file]
                    print(f"{cheking_file}: file checked, checksums matched\nSHA-1: {ch_sum}\n")
                else:
                    bad_files += [cheking_file]
                    print(f"File: {cheking_file} was changed or CORRUPTED!!!\nCalculated SHA-1: {ch_sum}\nbut the database for this file stores SHA-1:\n{old_sha}\n")

            elif len(old_sha) == 64:
                # the database stores SHA-256 checksums
                ch_sum = sha256_calc(check_dir + cheking_file)

                print(f"Calculating SHA-256 for {int(clear_list.index(cheking_file)/2+1)} of {int(len(clear_list)/2)} files in the list")

                if old_sha == ch_sum:
                    good_files += [cheking_file]
                    print(f"{cheking_file}: file checked, checksums matched\nSHA-256: {ch_sum}\n")
                else:
                    bad_files += [cheking_file]
                    print(f"File: {cheking_file} was changed or CORRUPTED!!!\nCalculated SHA-256: {ch_sum}\nbut the database for this file stores SHA-256:\n{old_sha}\n")

            elif len(old_sha) == 128:
                # the database stores SHA-512 checksums
                ch_sum = sha512_calc(check_dir + cheking_file)

                print(f"Calculating SHA-512 for {int(clear_list.index(cheking_file)/2+1)} of {int(len(clear_list)/2)} files in the list")

                if old_sha == ch_sum:
                    good_files += [cheking_file]
                    print(f"{cheking_file}: file checked, checksums matched\nSHA-512: {ch_sum}\n")
                else:
                    bad_files += [cheking_file]
                    print(f"File: {cheking_file} was changed or CORRUPTED!!!\nCalculated SHA-512: {ch_sum}\nbut the database for this file stores SHA-512:\n{old_sha}\n")
            
            else:
                print("Database error!")
                exit()


    # number of files that are in the list but not in the folder
    number_of_lost_files = int(len(clear_list)/2)-(len(good_files)+len(bad_files))

    print("Total summary:")
    print(17*"-")
    print (f"{len(good_files)} file(s) passed verification test\n{len(bad_files)} file(s) failed verification\n{number_of_lost_files} file(s) not found in the folder\n")

    if len(bad_files) > 0:
        print ("Checksums do not match for these files:")
        for b_f in bad_files:
            print(b_f)

    exit()

'''
If the specified [dir] is NOT a path to a database file, the code below will run
Works in checksums calculation mode in the specified folder
'''

folder_name = os.path.basename(dir) # when need to use only the folder name instead of the full path

if dir == '':
    dir = os.path.abspath(os.getcwd())
    folder_name = os.path.basename(dir)

if os.path.isdir (dir) == False:
    #if the user entered a file path instead of a folder path, compute a checksum for that file
    if os.path.isfile (dir) == True:
        print (f"\n{dir} is a file, NOT a folder!\nCalculating checksum for it.\n\nSHA1: {sha1_calc(dir)}")
    else:
        print ("Entered path does not exist.")
    exit()

# list of all files in all subfolders
files = list()
for (dirpath, dirnames, filenames) in os.walk(dir):
    files += [os.path.join(dirpath, file) for file in filenames]

if len(files) == 0:
    print("NO files in this folder. There is nothing to do...")
    exit()

# filtering out old database's files (checksums_list_for_... .txt) if they are in the current folder
old_summaries = [filename for filename in os.listdir(dir) if filename.startswith("checksums_list_for")]
files = [x for x in files if os.path.basename(x) not in old_summaries] #list of all files without old checksums_list_for_... .txt files

# get size of all files in current folder
folder_size = 0
for fs in files:
    folder_size += os.path.getsize(fs)

dir = os.path.join(dir,'')

# to optimize disk usage, first write the database to ram
database_ram = list()

print(f"""{50*'-'}
This application allows you to calculate SHA-1, SHA-256 or SHA-512 checksums for all files in the specified folder.
Their list and their checksums will be saved to a file that can later be used to check data integrity.
SHA-1 is chosen by default due to its superior computational speed.
SHA-256 and SHA-512 are more reliable, but their computation is much slower
{50*'*'}
If you choose to use SHA-1 press Enter\nTo use SHA-256 enter [2]\nTo use SHA-512 enter [3]
{25*'*'}""")

choised_sha_type = input("Your choise is: ")
print(50*"-")

if choised_sha_type == '3':
    choised_sha_type = 'SHA-512'
    # calculating SHA512 checksums
    for current_file in files:
        displayed_filename = current_file.replace(dir, '') #so that not the entire path to the file is stored in the database, but relative to the specified directory
        print (f"Calculating SHA-512 for {files.index(current_file)+1} of {len(files)} files: {displayed_filename}")
        sha_sum = sha512_calc(current_file) + '\n'
        print (sha_sum)
        database_ram += [displayed_filename + '\n' + sha_sum + '\n']

elif choised_sha_type == '2':
    choised_sha_type = 'SHA-256'
    # calculating SHA256 checksums
    for current_file in files:
        displayed_filename = current_file.replace(dir, '') #so that not the entire path to the file is stored in the database, but relative to the specified directory
        print (f"Calculating SHA-256 for {files.index(current_file)+1} of {len(files)} files: {displayed_filename}")
        sha_sum = sha256_calc(current_file) + '\n'
        print (sha_sum)
        database_ram += [displayed_filename + '\n' + sha_sum + '\n']

else:
    # if the user entered nothing {pressed 'Enter' only} or entered something undefined, just choose the default value
    choised_sha_type = 'SHA-1'
    # calculating SHA1 checksums
    for current_file in files:
        displayed_filename = current_file.replace(dir, '') #so that not the entire path to the file is stored in the database, but relative to the specified directory
        print (f"Calculating SHA-1 for {files.index(current_file)+1} of {len(files)} files: {displayed_filename}")
        sha_sum = sha1_calc(current_file) + '\n'
        print (sha_sum)
        database_ram += [displayed_filename + '\n' + sha_sum + '\n']


database_filename = "checksums_list_for" + '_' + folder_name + "_" + datetime.now().strftime("%Y%m%d_%H_%M")+".txt"
database = open(dir + database_filename, "w", encoding="utf-8")
database.write (f"Checksums calculated for {len(files)} files with a total size of {converting_bytes(folder_size)} in the folder: {folder_name}\nThe list of files and {choised_sha_type} checksums are listed below:\n{54*'-'}\n\n")

# writing database to the file
for li in database_ram:
    database.write(li.replace('\\','/')) # if the script is running on Windows, bring the writed paths to the posix view ('\' --> '/')

database.close

if len(old_summaries) > 0:
    print(30*"-")
    if len(old_summaries) == 1:
        print(f"One old [checksums_list_for... .txt] file was found in the root of '{folder_name}' folder. It was excluded from the results.")
    else:
        print(f"{len(old_summaries)} old [checksums_list_for... .txt] files were found in the root of '{folder_name}' folder. They were excluded from the results.")

print(30*"-")
print(f"{choised_sha_type} calculated for {len(files)} files with a total size of {converting_bytes(folder_size)}.\nSummary is here: {database_filename}")
