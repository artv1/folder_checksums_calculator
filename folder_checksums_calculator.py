import os, hashlib, sys
from datetime import datetime

#sha1 calculating
def hash_calc(filename):
    with open(filename, "rb") as f:
        file_hash = hashlib.sha1()
        while chunk := f.read(65536):
            file_hash.update(chunk)
    return file_hash.hexdigest()

#terminal argument input
if len(sys.argv) > 1:
    # if argument contains spaces, use all arguments to build path
    joint_path = " ".join(sys.argv[1:])

    #if argument is path to folder or file, use it
    if os.path.isdir(joint_path) == True or os.path.isfile (joint_path) == True:
        dir = joint_path

    else:
        print (f"You have used the wrong argument '{sys.argv[1]}'. It should be the path to a folder or file")
        exit()

else:
    # if no argument detected
    dir = input("Enter folder: ") #getting the path to the working folder

folder_name = os.path.basename(dir) #when need to use only the folder name instead of the full path

if dir == '':
    dir = os.path.abspath(os.getcwd())
    folder_name = os.path.basename(dir)

if os.path.isdir (dir) == False:
    #if the user entered a file path instead of a folder path, compute a checksum for that file
    if os.path.isfile (dir) == True:
        print (f"\n{dir} is a file, NOT a folder!\nCalculating checksum for it.\n\nSHA1: {hash_calc(dir)}")
    else:
        print ("Entered path does not exist.")
    exit()

#list of all files in all subfolders
files = list()
for (dirpath, dirnames, filenames) in os.walk(dir):
    files += [os.path.join(dirpath, file) for file in filenames]

if len(files) == 0:
    print("NO files in this folder. There is nothing to do...")
    exit()


#filtering out old database's files (checksums_list_for_... .txt) if they are in the current folder
old_summaries = [filename for filename in os.listdir(dir) if filename.startswith("checksums_list_for")]
filtered = [x for x in files if os.path.basename(x) not in old_summaries]

files = filtered #list of all files without old checksums_list_for_... .txt files

dir = dir + '/' # some cosmetic

database_filename = "checksums_list_for" + '_' + folder_name + "_" + datetime.now().strftime("%Y%m%d_%H_%M")+".txt"
database_location = dir + database_filename
database = open (database_location, "w")
database.write (f"There are {len(files)} files in the folder: {folder_name}\nThe list of files and SHA1 checksums are listed below:\n{54*'-'}\n\n")

for current_file in files:
    displayed_filename = current_file.replace(dir, '') #so that not the entire path to the file is stored in the database, but relative to the specified directory
    print (f"Calculating SHA1 for: {displayed_filename}")
    sum = hash_calc(current_file) + '\n'
    print (sum)
    database.write (displayed_filename + '\n' + sum + '\n')

database.close

if len(old_summaries) > 0:
    print(30*"-")
    if len(old_summaries) == 1:
        print(f"One old [checksums_list_for... .txt] file was found in the root of '{folder_name}' folder. It was excluded from the results.")
    else:
        print(f"{len(old_summaries)} old [checksums_list_for... .txt] files were found in the root of '{folder_name}' folder. They were excluded from the results.")

print(30*"-")
print(f"SHA1 calculated for {len(files)} files.\nSummary is here: {database_filename}")
