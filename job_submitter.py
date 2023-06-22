import os
import sys
import time
import re



def input_manager():
    """\
    After user confirmation that they wish to start automatic job submission and entry of the genus and MAX_JOB_AMOUNT 
    this function wraps a function call of watchdog_boss() in a .sh file which is executed inside a screen. 
    The screen is closed after all jobs are done.

    Input Parameters
    ----------
    confirmation : str
        either y or n, something else prompts the function again
    genus : str
        Name of the genus for which jobs are to be submitted automatically

    """
    confirmation = input("Start automatic submission of all jobs now? y/n: ")
    
    yes = confirmation == "y" or confirmation == "yes"
    
    no = confirmation == "n" or confirmation == "no"
    
    if no:
        print("halting...")
        sys.exit()
        
    if yes:
        
        genus = input("Please enter genus name (should match the directory): ")
        
        jobs_dir = os.getcwd()
        
        jobs_content = os.listdir(jobs_dir)
        
        if not genus in jobs_content:
            print(jobs_content)
            print(f"Genus {genus} not found, typo?")
            input_manager()
            sys.exit()
        
        MAX_JOBS_AMOUNT = int(input("How many jobs should be submitted at a time? "))
    
        screen_name = genus + "_jobs"
    
        function_call = f"watchdog_boss(genus='{genus}', MAX_JOBS_AMOUNT={MAX_JOBS_AMOUNT})"
        
        command = f'python3.6 -c "from job_submitter import watchdog_boss; {function_call}"'
    
        with open(f"{screen_name}.sh", "w") as shell:
            
            shell.write(command + "\n")
    
        command = f'screen -dmS {screen_name} bash -c "bash {screen_name}.sh; exec sh"'
        
        print(command)

        os.system(command)
    
    else:
        print("Please enter either 'y' or 'n'")
        input_manager()



def watchdog_boss(genus:str, MAX_JOBS_AMOUNT:int):
    """\
    This function finds all undone jobs for the genus, divides the total amount of jobs by the maximum amount of 
    jobs to be run at a time (MAX_JOBS_AMOUNT) and then submits them in batches of size MAX_JOBS_AMOUNT. Completion
    of a job is indicated by a feedback file being created; the presence of which is checked for by watch_dog() 
    every ten minutes. After all jobs in a batch are completed, the next batch is submitted.

    Parameters
    ----------
    genus : str
        Name of the genus for which jobs are to be submitted automatically
    MAX_JOBS_AMOUNT : int
        maximum amount of jobs to be submitted at a time
    """
    MAX_JOBS_AMOUNT = int(MAX_JOBS_AMOUNT)
        
    jobs_dir = os.getcwd()

    genus_batches_dir = f"{jobs_dir}/{genus}/batches"

    dir_content = os.listdir(genus_batches_dir)

    batch_pattern = f"{genus}_batch" + r"_[\d]{1,}.sh$"

    batches = []

    for content in dir_content:
        batch = re.findall(batch_pattern, content)

        if len(batch) > 0:
            already_done = f"{batch[0]}_LOG_feedback" in dir_content

            if not already_done:

                batches.append(batch[0])

    job_list = []

    for i in range(0, len(batches), MAX_JOBS_AMOUNT):
        job_list.append(batches[i:i + MAX_JOBS_AMOUNT])

    print(f"found {len(batches)} jobs, submitting in batches of {MAX_JOBS_AMOUNT}")
    
    # os.system(f"echo {len(batches)}, {batches} >> undone_batches.txt")
    
    # os.system(f"echo {job_list} >> joblist.txt")

    for job in job_list:
        print(f"submitting {job}")
        for batch in job:
            with open(f"{genus_batches_dir}/{batch}", "r") as file:
                shell = file.readlines()

            for line in shell:
                if "walltime" in line:
                    max_runtime = int(line.split("=")[1].split(":")[0])

            if max_runtime > 48:
                queue_type = "long"
            elif max_runtime < 48:
                queue_type = "short"
            
            command = f"qsub -q {queue_type} {genus_batches_dir}/{batch}"
            print(command)

            os.system(command)
            print(f"{batch} submitted")

        while(not watchdog(job, genus_batches_dir)):
            if not watchdog(job, jobs_dir):
                
                for batch in job:
                    
                    os.system(f"mv {batch}_LOG {genus_batches_dir}/{batch}_LOG")
                    os.system(f"mv {batch}_LOG_feedback {genus_batches_dir}/{batch}_LOG_feedback")
                    
                continue
               
            time.sleep(10*60)

    screen_name = genus + "_jobs"
    
    os.system(f"screen -XS {screen_name} quit")
    
    return True



def watchdog(job_titles:list, job_dir:str):
    """\
    This function checks for the presence of the feedback files for a given list of jobs

    Parameters
    ----------
    job_titles : list
        list of jobs to be checked for completion
    job_dir : str
        directory of those jobs
    
    Returns
    -------
    jobs_all_done : bool
        True if all jobs are done, False if even one is not
    """
    jobs_all_done = True

    dir_content = os.listdir(job_dir)

    for job in job_titles:

        job_feedback = f"{job}_LOG_feedback"

        if not job_feedback in dir_content:
            print(f"{job} not yet done")
            jobs_all_done = False

    return jobs_all_done



    
    
    
def main():
    
    input_manager()
    



if __name__ == '__main__':
    main()
