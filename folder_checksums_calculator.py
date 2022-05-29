# https://github.com/artv1/folder_checksums_calculator

import os, hashlib, sys
from datetime import datetime

# sha calculating
def sha_calc(filename, sha_type):
    if sha_type == 'SHA-1':
        hash = hashlib.sha1()
    elif sha_type == 'SHA-256':
        hash = hashlib.sha256()
    elif sha_type == 'SHA-512':
        hash = hashlib.sha512()
    else:
        return 'Wrong SHA type'

    with open(filename, "rb") as f:
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

def filelist(thepath):
    # list of all files in all subfolders
    flist = list()
    for (dirpath, dirnames, filenames) in os.walk(thepath):
        flist += [os.path.join(dirpath, file) for file in filenames]

    # filtering out old database's files (checksums_list_for_... .txt) if they are in the current folder
    old_summaries = [filename for filename in os.listdir(thepath) if filename.startswith("checksums_list_for")]
    flist = [x for x in flist if os.path.basename(x) not in old_summaries] # list of all files without old checksums_list_for_... .txt files

    # get size of all files in current folder
    fsize = 0
    for fs in flist:
        fsize += os.path.getsize(fs)

    return flist, fsize, len(flist), len(old_summaries)

def folder_sha(path, folder_name):
    # getting values
    files, files_size, files_number, old_summaries_len = filelist(path)

    if files_number == 0:
        print("NO files in this folder. There is nothing to do...")
        exit()

    print(f"{50*'-'}\n{files_number} files with a total size of {converting_bytes(files_size)} were found.\n\n"
            "The program will calculate SHA-1/256/512 checksums for all of them.\n"
            "A list of files with their checksums will be saved and can be used to check the data integrity.\n\n"
            "SHA-1 is chosen by default due to its superior computational speed.\n"
            "SHA-256 and SHA-512 are more reliable, but their computation is slower.\n"
            f"{50*'*'}\nIf you choose to use SHA-1 press 'Enter'\nTo use SHA-256 enter [2]\nTo use SHA-512 enter [3]\n{25*'*'}")

    shatype = input("Your choise is: ")
    print(50*"-")

    if shatype == '3':
        shatype = 'SHA-512'
    elif shatype == '2':
        shatype = 'SHA-256'
    else:
        shatype = 'SHA-1'
    
    # to optimize disk usage, first write the database to ram
    database_ram = list()

    path = os.path.join(path,'')

    for current_file in files:
        displayed_filename = current_file.replace(path, '') #so that not the entire path to the file is stored in the database, but relative to the specified directory
        print(f"Calculating {shatype} for {files.index(current_file)+1} of {files_number} files: {displayed_filename}")
        sha_sum = sha_calc(current_file, shatype)
        print(sha_sum + '\n')
        database_ram += [displayed_filename + '\n' + sha_sum + '\n\n']

    database_filename = "checksums_list_for" + '_' + folder_name + "_" + datetime.now().strftime("%Y%m%d_%H_%M")+".txt"
    database = open(path + database_filename, "w", encoding="utf-8")
    database.write(f"Checksums calculated for {files_number} files with a total size of {converting_bytes(files_size)} in the folder: {folder_name}\nThe list of files and {shatype} checksums are listed below:\n{56*'-'}\n\n")

    # writing database to the file
    for li in database_ram:
        database.write(li.replace('\\','/')) # if the script is running on Windows, bring the writed paths to the posix view ('\' --> '/')

    database.close

    if old_summaries_len > 0:
        print(30*"-")
        if old_summaries_len == 1:
            print(f"One old [checksums_list_for... .txt] file was found in the root of '{folder_name}' folder. It was excluded from the results.")
        else:
            print(f"{old_summaries_len} old [checksums_list_for... .txt] files were found in the root of '{folder_name}' folder. They were excluded from the results.")

    print(30*"-")
    print(f"{shatype} calculated for {files_number} files with a total size of {converting_bytes(files_size)}.\nSummary is here: {database_filename}")

def file_sha(path, file_name):
    print(f"{40*'-'}\n'{file_name}' is a file, NOT a folder!\nCalculating checksums for it.\n")
    print(f"SHA-1:   {sha_calc(path, 'SHA-1')}\nSHA-256: {sha_calc(path, 'SHA-256')}\nSHA-512: {sha_calc(path, 'SHA-512')}")

def verification_sha(path):
    print (f"{50*'-'}\nYou've selected a DATABASE file: {os.path.basename(path)}\nLet's begin verification\n{50*'-'}\n")

    # now 'path' is path to database file, so open it
    dfile = open(path, encoding="utf-8")

    # path to the parent folder of the database file
    check_dir = os.path.join(os.path.dirname(path),'')

    d_content = dfile.readlines()
    raw_data = d_content[4:]

    new_list = [s.replace("\n", "") for s in raw_data]
    clear_list = list(filter(None, new_list)) # list of files and hashsums only

    files_inlist_number = int(len(clear_list)/2)

    good_files = list() # files that have been verified against database
    bad_files = list() # files that have NOT been verified against database
    lost_files = list() # files that are in the list but not in the folder

    for cheking_file in clear_list[::2]:
        if os.path.isfile(check_dir + cheking_file):
            
            old_sha = clear_list[clear_list.index(cheking_file)+1] # next element is old checksum from database
            
            if len(old_sha) == 40:
                shatype = 'SHA-1'
            elif len(old_sha) == 64:
                shatype = 'SHA-256'
            elif len(old_sha) == 128:
                shatype = 'SHA-512'
            else:
                print("Database error!")
                exit()

            print(f"Calculating {shatype} for {int(clear_list.index(cheking_file)/2+1)} of {files_inlist_number} files in the list")
            ch_sum = sha_calc(check_dir + cheking_file, shatype)

            if old_sha == ch_sum:
                good_files += [cheking_file]
                print(f"{cheking_file}: file checked, checksum matched\n{shatype}: {ch_sum}\n")
            else:
                bad_files += [cheking_file]
                print(f"File: {cheking_file} was changed or CORRUPTED!!!\nCalculated {shatype}: {ch_sum}\nbut the database for this file stores {shatype}:\n{old_sha}\n")
            
        else:
            lost_files += [cheking_file]

    # getting a list of files in the current folder
    files = filelist(check_dir)[0]

    # deleting part of path string before 'current folder', because only relative paths are stored in the database
    files_ralative_path = [cf.replace(check_dir, '') for cf in files]

    # files that are present in the folder but not in the database
    new_files = [nf for nf in files_ralative_path if nf not in good_files and nf not in bad_files]

    print(f"""
    Total summary:
    {17*'-'}
    {len(good_files)} file(s) passed verification test
    {len(bad_files)} file(s) failed verification
    {len(lost_files)} file(s) from the list not found in the folder
    {len(new_files)} new file(s) were found in the folder\n""")

    if len(bad_files) > 0:
        inp_ch = input("To display a list of files that FAILED verification, type '1': ")
        if inp_ch == '1':
            print (f"Checksums do not match for these files:\n{40*'-'}")
            for f in bad_files:
                print(f)
            print(40*'-')

    if len(lost_files) > 0:
        inp_ch = input("To display a list of lost or REMOVED files, type '1': ")
        if inp_ch == '1':
            print (f"Files that are in the database but not in the folder:\n{40*'-'}")
            for f in lost_files:
                print(f)
            print(40*'-')

    if len(new_files) > 0:
        inp_ch = input("To display a list of NEW files, type '1': ")
        if inp_ch == '1':
            print (f"Files that are present in the folder but not in the database:\n{40*'-'}")
            for f in new_files:
                print(f)
            print(40*'-')
    exit()

def path_input():
    #terminal argument input
    if len(sys.argv) > 1:
        # if argument contains spaces, use all arguments to build path
        joint_path = " ".join(sys.argv[1:])

        # if the argument is a path to a folder or file, use it
        if os.path.isdir(joint_path) or os.path.isfile (joint_path):
            path = joint_path
        else:
            print (f"Path '{joint_path}' not found.")
            exit()
    else:
        # if no argument detected
        path = input("Enter path: ") # getting the path to the working folder

    path = os.path.abspath(path)

    if path == '':
        path = os.path.abspath(os.getcwd())
    
    return path, os.path.basename(path) # full path and only the folder or file name

if __name__ == '__main__':
    
    path,fname = path_input()
    
    if os.path.isfile(path):
        # Check if the specified [path] is the path to the database file.
        # If so, then the program works in the mode of checking existing files for compliance with the database.
        if fname.startswith("checksums_list_for_"):
            verification_sha(path)
        else:
            file_sha(path,fname)

    elif os.path.isdir(path):
        # calculating checksums in the specified folder
        folder_sha(path,fname)
    else:
        print("Entered path does not exist.")
        exit()