import os
from subprocess import Popen, PIPE, run, call
import sys
import time
import re
# def submitting_shell():
#     """\
#     Submits all jobs of a user-specified genus found in the {genus}/batches directory
#     """
#     dir_content = os.listdir()
#     gattung_name = input("Enter genus for which you want to submit jobs:").capitalize()
#     cwd = os.getcwd()

#     if gattung_name in dir_content:
#         os.chdir(f"{gattung_name}/batches")
#         batches = os.listdir()
#         print(f"Found {len(batches)} batches, submitting...")
        
#         for batch in batches:

#             os.system(f"qsub -q short {batch}")
#             print(f"{batch} submitted")
        
#         print("Batches submitted. Overview")
#         os.system("qstat -u tu_zxozy01")

#     else:
#         return "No such genus present."



# def screen_creator(genus:str, jobs_dir:str):
#     which_screen_result = call(["which", "screen"])

#     if which_screen_result == 0:
#         print("screen installed")
#     else:
#         print("screen not installed")
#         sys.exit()

#     screen_name = f"{genus}_job_submitter"

#     #screen = run(["/usr/bin/screen", "-S", f"{screen_name}"], shell=True, stdin=PIPE, stdout=PIPE)
#     #screen = Popen(["/usr/bin/screen", "-S", f"{screen_name}"], shell=True, stdin=PIPE, stdout=PIPE)
#     screen = Popen(f"/usr/bin/screen -S {screen_name}", shell=True, start_new_session=True, stdin=PIPE, stdout=PIPE)

#     #test = Popen(["echo", "pls be in screen"], shell=True, stdin=screen.stdout)

    
#     statusProc = run('screen -ls', shell=True, stdout=PIPE, stdin=PIPE)
#     statusString = statusProc.stdout.decode('ascii')
#     print(statusString)



def manager(genus:str, jobs_dir:str):

    genus_batches_dir = f"{jobs_dir}/{genus}/batches"

    dir_content = os.listdir(genus_batches_dir)


    batch_pattern = f"{genus}_batch" + r"_[\d]{1,}.sh$"
    print(batch_pattern)

    batches = []

    for content in dir_content:
        batch = re.findall(batch_pattern, content)

        if len(batch) > 0:

            batches.append(batch[0])



    MAX_JOBS_AMOUNT = 5

    job_list = []

    for i in range(0, len(batches), MAX_JOBS_AMOUNT):
        job_list.append(batches[i:i + MAX_JOBS_AMOUNT])
    
    print(f"found {len(batches)} jobs, submitting in batches of {MAX_JOBS_AMOUNT}")

    for job in job_list:
        for batch in job:
            os.system(f"qsub -q short {batch}")
            print(f"{batch} submitted")

        while(not watchdog(job)):
            time.sleep(10*60)
            

    




def watchdog(job_titles:str, job_dir:str):
    jobs_all_done = True

    dir_content = os.listdir(job_dir)

    for job in job_titles:

        job_feedback = f"{job}_LOG_feedback"

        if not job_feedback in dir_content:
            print(f"{job} not yet done")
            jobs_all_done = False

    return jobs_all_done



    
    
    
def main():
    #submitting_shell()

    #screen_creator("Kosakonia", "/beegfs/work/tu_zxozy01")

    manager("Kosakonia", "/beegfs/work/tu_zxozy01/jobs")


if __name__ == '__main__':
    main()
