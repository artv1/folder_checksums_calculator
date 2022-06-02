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

# list of all files
def filelist(thepath):
    
    flist = list()
    for (dirpath, dirnames, filenames) in os.walk(thepath):
        flist += [os.path.join(dirpath, file) for file in filenames]

    # filtering out old database's files (checksums_listfor_... .txt) if they are in the current folder
    old_summaries = [filename for filename in os.listdir(thepath) if filename.startswith("checksums_")]
    flist = [x for x in flist if os.path.basename(x) not in old_summaries] # list of all files without old checksums_listfor_... .txt files

    # get size of all files in current folder
    fsize = 0
    for fs in flist:
        fsize += os.path.getsize(fs)

    return flist, fsize, len(flist), len(old_summaries)

# calculate SHA for all files in folder
def folder_sha(path):

    path = os.path.abspath(path)
    folder_name = os.path.basename(path)

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
        database_ram += [current_file + '\n' + sha_sum + '\n\n']

    database_filename = "checksums_listfor" + '_' + folder_name + "_" + datetime.now().strftime("%Y%m%d_%H_%M")+".txt"
    database_header = [f"Checksums calculated for {files_number} files with a total size of {converting_bytes(files_size)} in the folder: ", f"{folder_name}\n",
                       f"The list of files and {shatype} checksums are listed below:\n{56*'-'}\n\n"]

    outcome = write_summary(path, database_filename, database_header+database_ram, path)

    if old_summaries_len > 0:
        print(30*"-")
        if old_summaries_len == 1:
            print(f"One old [checksums_... .txt] file was found in the root of '{folder_name}' folder. It was excluded from the results.")
        else:
            print(f"{old_summaries_len} old [checksums_... .txt] files were found in the root of '{folder_name}' folder. They were excluded from the results.")

    print(30*"-")
    print(f"{shatype} calculated for {files_number} files with a total size of {converting_bytes(files_size)}.")
    if outcome:
        print(f"Summary is here: {database_filename}")
    else:
        print("But, the summary is NOT saved!")

# calculate SHA for a single file
def file_sha(path):
    print(f"{40*'-'}\n'{os.path.basename(path)}' is a file.\nIts size is {converting_bytes(os.path.getsize(path))}\nCalculating checksums for it.\n")

    sha1 = sha_calc(path, 'SHA-1')
    sha256 = sha_calc(path, 'SHA-256')
    sha512 = sha_calc(path, 'SHA-512')

    summary = [f"SHA-1:   {sha1}\n",f"SHA-256: {sha256}\n",f"SHA-512: {sha512}\n"]

    for i in summary:
        print(i.replace('\n',''))

    if input("\nTo SAVE summary to a file, type '1': ") == '1':
        summary = [f"{os.path.basename(path)}\n", f"{converting_bytes(os.path.getsize(path))}\n\n"] + summary
        summary_filename = "checksums_forfile_"+os.path.basename(path)+'_'+datetime.now().strftime("%Y%m%d_%H_%M")+".txt"
        if write_summary(os.path.dirname(path), summary_filename, summary, path):
            print("Saved Successfully")
        
# checking the existing database
def verification_sha(path):
    print (f"{50*'-'}\nYou've selected a DATABASE file: {os.path.basename(path)}\nLet's begin verification\n{50*'-'}\n")

    # path to the parent folder of the database file
    check_dir = os.path.join(os.path.dirname(path),'')

    # now 'path' is path to database file, so open it
    try:
        with open(path, encoding="utf-8") as dfile:
            d_content = dfile.readlines()
            raw_data = d_content[4:]
    except:
        print("Database file is not readable")
        exit()

    # verification SHA-256 for a single file Summary
    if os.path.basename(path).startswith("checksums_forfile"):
        # extracting filename from summary
        filename = d_content[0].replace("\n","")
        if not os.path.isfile(check_dir+filename):
            check_dir=''
        if os.path.isfile(check_dir+filename):
            for i in d_content:
                if i.startswith('SHA-256: '):
                    # extracting old checksum from summary
                    oldsha = i.replace("\n","").replace('SHA-256: ','')
                    if len(oldsha) == 64:
                        shatype = 'SHA-256'
                        newsha = sha_calc(check_dir+filename, shatype)
                        if newsha == oldsha:
                            print(f"{filename}: file checked, checksum MATCHED\n{shatype}: {newsha}\n")
                        else:
                            print(f"File: {filename} was changed or CORRUPTED!!!\nCalculated {shatype}:\n{newsha}\n")
                            print(f"Stored in Summary {shatype}:\n{oldsha}\n")
                            if input(f"{40*'*'}\nTo calculate the actual checksums and generate a new summary, type '1': ") == '1':
                                file_sha(check_dir+filename)
            exit()
    elif not os.path.basename(path).startswith("checksums_list"):
        exit()

    new_list = [s.replace("\n", "") for s in raw_data]
    clear_list = list(filter(None, new_list)) # list of files and hashsums only
    
    full_path_used = False
    # check if the database stores full paths instead of relative ones
    for i in clear_list[::2]:
        if os.path.isfile(i) and not os.path.isfile(check_dir+i):
            full_path_used = True
            check_dir = ''
            # if so, find and extract the full path from the first line (it is a part of string after ': ' in it)
            firstline = d_content[0]
            for y in firstline:
                if y == ':':
                    x = firstline.index(y)+2
                    if os.path.isdir(firstline[x:-1]):
                        check_dir_fullpath = firstline[x:-1]
                    else:
                        return 'Database error'
            break
        elif os.path.isfile(check_dir+i):
            full_path_used = False
            break

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

    if full_path_used:
        check_dir = check_dir_fullpath
        print(check_dir)

    # getting a list of files in the current folder
    files = filelist(check_dir)[0]

    if full_path_used:
        files_relative_path = files
    else:
        # deleting part of path string before 'current folder', because only relative paths are stored in the database
        files_relative_path = [cf.replace(check_dir, '') for cf in files]

    # files that are present in the folder but not in the database
    new_files = [nf for nf in files_relative_path if nf not in good_files and nf not in bad_files]

    len_good_files = len(good_files)
    len_bad_files = len(bad_files)
    len_lost_files = len(lost_files)
    len_new_files = len(new_files)

    print(f"""
    Total summary:
    {17*'-'}
    {len_good_files} file(s) passed verification test
    {len_bad_files} file(s) failed verification
    {len_lost_files} file(s) from the list not found in the folder
    {len_new_files} new file(s) were found in the folder\n""")

    if len_bad_files > 0 or len_lost_files > 0 or len_new_files > 0:
        print("The contents of the folder are DIFFERENT from the database.")
        inp_ch = input("To recalculate it type '1': ")
        if inp_ch == '1':
            folder_sha(check_dir)
        else:
            if len_bad_files > 0:
                inp_ch = input("To display a list of files that FAILED verification, type '1': ")
                if inp_ch == '1':
                    print (f"Checksums do not match for these files:\n{40*'-'}")
                    for f in bad_files:
                        print(f)
                    print(40*'-')

            if len_lost_files > 0:
                inp_ch = input("To display a list of lost or REMOVED files, type '1': ")
                if inp_ch == '1':
                    print (f"Files that are in the database but not in the folder:\n{40*'-'}")
                    for f in lost_files:
                        print(f)
                    print(40*'-')

            if len_new_files > 0:
                inp_ch = input("To display a list of NEW files, type '1': ")
                if inp_ch == '1':
                    print (f"Files that are present in the folder but not in the database:\n{40*'-'}")
                    for f in new_files:
                        print(f)
                    print(40*'-')
            exit()

# writing database (or summary) to the file
def write_summary(folder_path, filename, content_list, full_path):
    short_path = True
    file_content = list()

    while True:
        folder_path = os.path.abspath(folder_path)
        path = os.path.join(folder_path,'')
        
        if short_path:
            for i in content_list:
                # only relative paths are stored in the database normally
                file_content += [i.replace(path, '')]
        else:
            # if the database cannot be written to the current folder, full paths are used
            # if full paths to files are stored in the database, then the full path to the folder should also be written in the db-header
            # this full folder path will be used for data verification
            file_content = content_list
            if '--' in file_content[2]:
                file_content[1] = os.path.abspath(full_path)+'\n'
            if os.path.isfile(full_path):
                file_content[0] = full_path + '\n'

        try:
            with open (path + filename, "w", encoding="utf-8") as summary:
                for i in file_content:
                    summary.write(i.replace('\\','/')) # if the script is running on Windows, bring the writed paths to the posix view ('\' --> '/')
            outcome = True
            break

        except:
            print(f"{40*'*'}\nThe summary-database file cannot be saved in the folder: '{folder_path}'\nEnter a path to another folder, or leave the field blank to skip saving the file.")
            folder_path = input('Input another path: ')
            short_path = False
            if folder_path == '':
                outcome = False
                break
    
    return outcome

def path_input():
    #terminal argument input
    if len(sys.argv) > 1:
        path = " ".join(sys.argv[1:]) # if argument contains spaces, use all arguments to build path
    # if no argument detected
    else:
        path = input("Enter path: ")

    while True:
        if path == '':
            path = os.getcwd()
            print(f"Current folder selected: '{path}'")
        if os.path.exists(os.path.abspath(path)):
            break
        else:
            path = input("Not found! Enter another path: ") # getting the path to the working folder
    
    return os.path.abspath(path)

if __name__ == '__main__':
    
        path = path_input()
        
        if os.path.isfile(path):
            # Check if the specified [path] is the path to the database file.
            # If so, then the program works in the mode of checking existing files for compliance with the database.
            if os.path.basename(path).startswith("checksums_"):
                verification_sha(path)
            else:
                file_sha(path)

        elif os.path.isdir(path):
            # calculating checksums in the specified folder
            folder_sha(path)
        else:
            print("Path error")