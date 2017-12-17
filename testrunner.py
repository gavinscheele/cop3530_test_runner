import os
import zipfile
import shutil
import re
import sys
import subprocess

BASE_DIR = "/cise/homes/gavin/Desktop/project2/"
SUBMISSION_DIR = BASE_DIR + "submissions/"
TEST_DIR = BASE_DIR + "testDir/"
TMP_DIR = BASE_DIR + "tmpDir/"
SRC_DIR = TEST_DIR + "src/"
INVALID_DIR = BASE_DIR + "invalidDir/"
ERROR_FILE_DIR = "errors.txt"
TEST_OUTPUT_DIR = BASE_DIR + "testOutput/"

def is_correct_format(aZip):
    found = False
    for filename in aZip.namelist():
        if re.search("project_2\/*", filename.lower()):
            found = True
            break
    return found

#def move_to_invalid_dir(error_file, student_name, aZip):
#    error_file.write(student_name + " submission format invalid. Moving to invalid directory.\n")
#    os.system('mv ' + aZip.filename + ' ' + INVALID_DIR)
    # aZip.extractall(INVALID_DIR + "/" + aZip.filename)

def delete_if_exists(aPath):
    if os.path.isdir(aPath):
        shutil.rmtree(aPath)
    if os.path.exists(aPath):
        os.remove(aPath)

def move_to_src_dir(aZip):
    aZip.extractall(TMP_DIR)
    old_dir = os.getcwd()
    os.chdir(TMP_DIR)
    os.system("mkdir -p " + SRC_DIR)
    os.system("find . -name '*.h' -exec mv {} " + SRC_DIR + " \;")
    os.chdir(old_dir)
    delete_if_exists(TMP_DIR)

def make_lists(file_path, student_name):
    os.system("make clean > /dev/null")
    lists = ["required", "group1", "group2", "group3"]
    for list_name in lists:
        os.system("make " + list_name + " >> " + file_path + " 2>&1")
    return lists

def run_tests_for_lists(file_path, student_name, lists):
    dir_path = TEST_OUTPUT_DIR + student_name + "/"
    for list_name in lists:
        os.system("echo \'TESTING " + list_name + "\' >> " + file_path)
        if not os.path.isfile("./" + list_name):
            print(list_name + " did not compile for " + student_name)
            continue
        os.system("cp " + list_name + " " + dir_path)
        p = subprocess.Popen("./" + list_name + " >> " + file_path + " 2>&1", shell=True)
        try:
            p.wait(timeout=6)
        except subprocess.TimeoutExpired:
            p.kill()
            p.communicate()
            os.system("touch " + dir_path + "timeout")
            print(student_name + " tests timed out.")
        #os.system("./" + list_name + " >> " + file_path + " 2>&1")

def run_valgrind_for_lists(file_path, lists):
    for list_name in lists:
        if not os.path.isfile("./" + list_name):
            continue
        os.system("touch " + file_path)
        p = subprocess.Popen("/usr/bin/valgrind --leak-check=yes --log-file=\'" + file_path + "\' ./" + list_name + " > /dev/null", shell=True)
        try:
            p.wait(timeout=20)
        except subprocess.TimeoutExpired:
            p.kill()
            p.communicate()
            print("valgrind timed out")

def run_tests(student_name):
    prev_wd = os.getcwd()
    os.chdir(TEST_DIR)
    dir_path = TEST_OUTPUT_DIR + student_name + "/"
    os.system("mkdir -p " + dir_path)    
    compilation_file_path = dir_path + student_name + "_compilation.txt"
    test_output_path = dir_path + student_name + "_tests.txt"
    valgrind_output_path = dir_path + student_name + "_valgrind.txt"
    delete_if_exists(compilation_file_path)
    delete_if_exists(test_output_path)
    delete_if_exists(valgrind_output_path)
    lists = make_lists(compilation_file_path, student_name)
    run_tests_for_lists(test_output_path, student_name, lists)
    run_valgrind_for_lists(valgrind_output_path, lists)

    os.system("make clean > /dev/null")    
    os.chdir(prev_wd)
    
def get_student_name_for_zip(aZip):
    return aZip.filename.split('_')[0]

delete_if_exists(ERROR_FILE_DIR)
delete_if_exists(SRC_DIR)
delete_if_exists(INVALID_DIR)

os.system("mkdir -p " + SRC_DIR)
os.system("mkdir -p " + INVALID_DIR)

ERROR_FILE = open(ERROR_FILE_DIR, "a")

os.chdir(SUBMISSION_DIR)
for zipname in os.listdir('.'):
    myZip = zipfile.ZipFile(zipname)
    student_name = get_student_name_for_zip(myZip)  
    print("Running tests for student: " + student_name)  
    #if not is_correct_format(myZip):
    #    move_to_invalid_dir(ERROR_FILE, student_name, myZip)
    #    continue

    move_to_src_dir(myZip)
    run_tests(student_name)
    delete_if_exists(SRC_DIR)
