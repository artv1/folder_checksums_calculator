# https://github.com/artv1/folder_checksums_calculator

import os, hashlib, sys, json
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

    try:
        with open(filename, "rb") as f:
            while chunk := f.read(65536):
                hash.update(chunk)
        return hash.hexdigest()
    except:
        return 'File read error'

# converting bytes to readable form
def converting_bytes(bytes):
    if not isinstance(bytes,int):
        return "Convertation impossible, variable must be an integer number of bytes"
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

# decorative border of the first and last line
def decorator(listof_strings, decor_symbol):
    max_len = 0
    for i in listof_strings:
        if len(i) > max_len:
            max_len = len(i)
    print(max_len*decor_symbol)
    for i in listof_strings:
        print(i)
    print(max_len*decor_symbol)

# list of all files without existing database files
def filelist_fullpath(thepath):
    try:
        flist=list()
        if os.sep == '/':
            for (dirpath, dirnames, filenames) in os.walk(thepath):
                flist += [os.path.join(dirpath, file) for file in filenames if not os.path.basename(file).startswith("shadata_")]
        else:
            for (dirpath, dirnames, filenames) in os.walk(thepath):
                flist += [os.path.join(dirpath, file).replace(os.sep, '/') for file in filenames if not os.path.basename(file).startswith("shadata_")]
        return flist
    except:
        print("Error getting list of files. The folder is not accessible")
        exit()

# list of all files without existing database files: RELATIVE PATHS
def filelist_relpath(path):
    try:
        files_relative_path = [os.path.relpath(os.path.join(dirpath, file), path).replace(os.sep,'/') for (dirpath, dirnames, filenames) \
            in os.walk(path) for file in filenames if not os.path.basename(file).startswith("shadata_")]

        return files_relative_path
    except:
        print("Error getting list of files. The folder is not accessible")
        exit()

# returns: os.path.join("folder",'').replace(os.sep,'/')
def genform(folder):
    return os.path.join(folder,'').replace(os.sep,'/')

# convert list of files from relative path view 'folder/file' to full path /home/user/folders.../file
def tofull_path(path_prefix, filelist):
    prefix = genform(path_prefix)
    filelist_fullpath = [prefix+file for file in filelist]
    return filelist_fullpath

# calculate size of all files in the list, returns: [0] size in bytes, [1] size in readable form
def filelist_size(flist):
    try:
        fsize = 0
        for fs in flist:
            fsize += os.path.getsize(fs)
        return fsize, converting_bytes(fsize)
    except:
        return 0,"Unable to get file size"

# calculation SHA for list of files, returns: [Dict{files:checksums}, [List of Unreadable files...], [List of Lost files...]]
def calc_sha_list(relative_folder,files,shatype):
    files_number = len(files)
    sha_data = dict() # dictionary with files for which checksums were calculated
    unreadable_files = list() # list of files with read errors or lack of access
    relative_folder = genform(relative_folder)

    # checking files existence, list of non-existent files
    lostfiles = [f for f in files if not os.path.isfile(f)]
    
    if len(lostfiles) > 0:
        files = [f for f in files if f not in lostfiles]
        
    i=0
    for current_file in files:
        i+=1
        #so that not the entire path to the file is stored in the database, but relative to the specified directory
        stored_filename = current_file.replace(relative_folder, '')
        if len(stored_filename) > 25:
            displayed_filename = stored_filename[:25] + '...'
        else:
            displayed_filename = stored_filename

        print(f"\rCalculating {shatype} for: {i} of {files_number} files: {displayed_filename}\033[K", end='')
        
        sha_sum = sha_calc(current_file, shatype)

        if sha_sum == 'File read error':
            unreadable_files.append(stored_filename)
            print("\r!!!UNREADABLE file!!!\033[K", end='')
            continue

        sha_data[stored_filename]=sha_sum


    print("\rFile processing complete\033[K") # '\033[K' clearing line after the string

    return sha_data, unreadable_files, lostfiles

# calculate SHA for all files in folder
def folder_sha(path):
    path = os.path.abspath(path)
    folder_name = os.path.basename(path)

    # getting values
    files = filelist_fullpath(path)
    files_size = filelist_size(files) # [0] is size in bytes, [1] in readable form
    files_number = len(files)

    if files_number == 0:
        return "NO files in this folder. There is nothing to do..."

    text = [f"{files_number} files with a total size of {files_size[1]} were found.",
            "The program will calculate SHA-1/256/512 checksums for all of them.\n",
            "Output JSON Database of checksums can be used to check the data integrity.",
            "SHA-1 is chosen by default due to its superior computational speed.",
            "SHA-256 and SHA-512 are more reliable, but their computation is slower.\n",
            "If you choose to use SHA-1 press 'Enter'",
            "To use SHA-256 enter '2'", "To use SHA-512 enter '3'"]

    decorator(text,'-')

    shatype = input("Your choise is: ")

    if shatype == '3':
        shatype = 'SHA-512'
    elif shatype == '2':
        shatype = 'SHA-256'
    else:
        shatype = 'SHA-1'

    print(f"{shatype}")
    
    sha_data, read_error_flist, lostfiles = calc_sha_list(path,files,shatype)

    read_error_count = len(read_error_flist)

    processed_filelist = tofull_path(path, sha_data.keys())
    processed_filelist_size = filelist_size(processed_filelist)[1]

    database_filename = f"shadata_listfor_{folder_name}.json"

    print(f"{shatype} calculated for {len(processed_filelist)} files with a total size of {processed_filelist_size}.")
    if read_error_count > 0:
        print(f"{read_error_count} read error(s) occured")

    d1 = {"Folder":folder_name, "Files number":len(processed_filelist), "Total size":processed_filelist_size,
        "SHA type":shatype, "Working folder":"Relative", "Updated":""}

    if write_summary(path, database_filename, [d1, sha_data, {"Unreadable files":read_error_flist}]):
        print(f"Summary is here: {database_filename}")
    else:
        print("!!! the summary is NOT saved !!!")

    return "Done"

# calculate SHA for a single file
def file_sha(file_path):
    file_name = os.path.basename(file_path)
    file_size = converting_bytes(os.path.getsize(file_path))

    text = [f"{file_name}' is a file.", f"Its size is {file_size}", "Calculating checksums for it."]
    decorator(text, '.')

    sha1 = sha_calc(file_path, 'SHA-1')
    if sha1 == "File read error":
        return "File read error. Unable to calculate checksum"
    sha256 = sha_calc(file_path, 'SHA-256')
    sha512 = sha_calc(file_path, 'SHA-512')

    summary = {"SHA-1":sha1,"SHA-256":sha256,"SHA-512":sha512}

    for i in summary:
        print(f"{i}: {summary[i]}")

    if input("\nTo SAVE summary to a file, type '1': ") == '1':
        d1 = {"Filename":file_name, "Size":file_size, "Working folder":"Relative"}
        summary_filename = f"shadata_forfile_{file_name}.json"
        if write_summary(os.path.dirname(path), summary_filename, [d1, summary]):
            print("Saved Successfully")
    
    return "Done"
        
# checking the existing database
def verification_list(database_file_path):
    try:
        with open(database_file_path) as dfile:
            stored_data = json.load(dfile)
    except:
        return "Database file is not readable"

    # stored Dict {files:sha}
    stored_filelist = stored_data[1]
    number_of_files = len(stored_filelist)
    shatype = stored_data[0]["SHA type"]

    # files with access/read error while creating database
    stored_unreadable_filelist = stored_data[2]["Unreadable files"]

    # check if the database stores full paths instead of relative ones
    if stored_data[0]["Working folder"] == "Relative":
        full_path_used = False
        # path to the parent folder of the database file
        check_dir = genform(os.path.dirname(database_file_path))
    else:
        full_path_used = True
        wdir = stored_data[0]["Working folder"]
        if os.path.isdir(wdir):
            check_dir = wdir
        else:
            return 'Working folder not available'

    text = [f"You have selected a database file with a list of {number_of_files} files",
            f"Total size of the files: {stored_data[0]['Total size']}"]
    
    decorator(text, '-')
    
    if full_path_used:
        print(f"Working folder: {check_dir}\n")
    
    if input("To START verification, type '1' ") != '1':
        return "Verification canceled by user"

    # database stores only relative paths, so conversion required
    stored_filelist_fullpath = tofull_path(check_dir, stored_filelist.keys())

    # adding previously 'unreadable' filelist to overall list
    if len(stored_unreadable_filelist) > 0:
        stored_filelist_fullpath.extend(tofull_path(check_dir, stored_unreadable_filelist))

    # calculating SHA for stored file list
    new_data = calc_sha_list(check_dir,stored_filelist_fullpath,shatype)
    list_todelete = new_data[2] # files that are in the list but not in the folder
    upd_filelist=dict() # Dict{file:sha} with updated SHA data, files whose checksums are different from the database

    if new_data[0] == stored_filelist:
        filelist_changed = False
    else:
        filelist_changed = True

        for i in new_data[0].keys():
            if i in stored_filelist.keys():
                if new_data[0][i] == stored_filelist[i]:
                    continue
                else:               
                    upd_filelist[i] = new_data[0][i]
            else:
                print(f"previously unredable {i} is now readable")
    
    # getting a list of files in the current folder
    files = filelist_relpath(check_dir)

    # files that are present in the folder but not in the database
    new_files = [f for f in files if f not in new_data[0].keys() and f not in new_data[1]]

    len_new_files = len(new_files)
    len_upd_filelist = len(upd_filelist)
    len_list_todelete = len(list_todelete)

    # if contents of the folder have not changed, exit function
    if not filelist_changed and len_new_files == 0:
        text = [f"All {number_of_files} files were SUCCESSFULLY VERIFIED with {shatype}",
                "The contents of the folder have not changed."]
        decorator(text, '=')
        return "Done"
    else:
        decorator(["The contents of the folder are DIFFERENT from the database."],'-')
        if len_upd_filelist > 0:
            if input(f"{len_upd_filelist} file(s) FAILED verification. To display a list of them, type '1': ") == '1':
                decorator(upd_filelist.keys(),'.')
        if len_list_todelete > 0:
            print(f"{len_list_todelete} file(s) from the database not found in the folder")
        if len_new_files > 0:
            print(f"{len_new_files} new file(s) were found in the folder")

        choise = input("To UPDATE database, type '1', to completely RECALCULATE, type '0': ")
        if choise == '0':
            folder_sha(check_dir)
            return "Done"

        elif choise == '1':

            if len_new_files > 0:
                # new files list with full path
                new_files = tofull_path(check_dir, new_files)
                
                decorator([f"{shatype} for {len_new_files} NEW file(s) of {filelist_size(new_files)[1]} will be calculated"],'.')
                new_files_data = calc_sha_list(check_dir,new_files,shatype)
                new_data[0].update(new_files_data[0])

                if len(new_files_data[1]) > 0:
                    new_data[1].extend(new_files_data[1])

            stored_data[0]["Files number"] = len(new_data[0])
            stored_data[0]["Total size"] = filelist_size(tofull_path(check_dir,new_data[0]))[1]

            if write_summary(check_dir,os.path.basename(database_file_path),[stored_data[0], new_data[0], {"Unreadable files":new_data[1]}]):
                print("Database successfully updated!")
        else:
            print("Skipped")
            
    return "Done"

# verification SHA-256 for a single file Summary
def verification_file(path):
    # now 'path' is path to summary file, so open it
    try:
        with open(path) as dfile:
            stored_data = json.load(dfile)
    except:
        return "Summary file is not readable"
    
    if stored_data[0]["Working folder"] == "Relative":
        # path to the parent folder of the summary file
        filename = genform(os.path.dirname(path)) + stored_data[0]["Filename"]
    else:
        filename = stored_data[0]["Working folder"] + stored_data[0]["Filename"]

    if os.path.isfile(filename):
        text = [f"Selected Summary for file: {filename}"]

        if "SHA-256" in stored_data[1]:
            oldsha = stored_data[1]["SHA-256"]
            text.extend(["Contains a stored SHA-256 checksum entry","Let's begin verification"])
            decorator(text, '.')
            shatype = 'SHA-256'
            newsha = sha_calc(filename, shatype)
            if newsha == 'File read error':
                return newsha
            if newsha == oldsha:
                print(f"{filename}: file checked, checksum MATCHED\n{shatype}: {newsha}\n")
            else:
                print(f"File: {filename} was changed or CORRUPTED!!!\nCalculated {shatype}:\n{newsha}\n")
                print(f"Stored in Summary {shatype}:\n{oldsha}\n")
                if input(f"{40*'*'}\nTo calculate the actual checksums and generate a new summary, type '1': ") == '1':
                    file_sha(filename)
        else:
            text.append("Does not contain a stored SHA-256 checksum entry")
            decorator(text, '-')
        return "Done"
    else:
        return "File specified in the summary does not exist"

# writing JSON database to the file
def write_summary(folder_tosave, filename, content):
    full_path = folder_tosave
    short_path = True
    content[0]["Updated"] = datetime.now().strftime("%Y/%m/%d %H:%M")

    while True:
        folder_tosave = os.path.abspath(folder_tosave)
        path = genform(folder_tosave)
        
        if not short_path:
            content[0]["Working folder"] = genform(full_path)

        try:
            with open(path + filename, "w") as jfile:
                json.dump(content, jfile, indent=4)
            return True

        except:
            text = [f"The summary-database file cannot be saved in the folder: '{folder_tosave}'",
                    "Enter a path to another folder, or leave the field blank to skip saving the file."]
            decorator(text,'-')
            while True:
                folder_tosave = input('Input another path: ')
                if folder_tosave == '':
                    return False
                elif os.path.isdir(folder_tosave):
                    short_path = False
                    break
                else:
                    print("Folder does not exist")
    
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
    resume = ''
        
    if os.path.isfile(path):
        # Check if the specified [path] is the path to the database file.
        # If so, then the program works in the mode of checking existing files for compliance with the database.
        if os.path.basename(path).startswith("shadata_list"):
            resume = verification_list(path)
        elif os.path.basename(path).startswith("shadata_forfile"):
            resume = verification_file(path)
        else:
            resume = file_sha(path)

    elif os.path.isdir(path):
        # calculating checksums in the specified folder
        resume = folder_sha(path)
    else:
        resume = "Path error"

    if resume != "Done" and resume != '':
        print(resume)
