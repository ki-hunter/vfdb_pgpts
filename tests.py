import time
import os
import re
import sys

def test_function():
    print(os.getcwd())

    time.sleep(1*60)

    os.system("touch first_LOG_feedback.txt")

    time.sleep(1*60)

    os.system("touch second_LOG_feedback.txt")

def test_2_function():

    time.sleep(1*60)

    os.system("touch third_LOG_feedback.txt")
    
    time.sleep(1*60)
    
    os.system("touch fourth_LOG_feedback.txt")


def test2():
    print("ALL DONE")


def input_manager():
    confirmation = input("Start automatic submission of all jobs now? y/n: ")
    
    yes = confirmation == "y" or confirmation == "yes"
    
    no = confirmation == "n" or confirmation == "no"
    
    if no:
        print("halting...")
        sys.exit()
        
    if yes:
        
        genus = input("Please enter genus name (should match the directory): ")
        
        MAX_JOBS_AMOUNT = int(input("How many jobs should be submitted at a time? "))
    
        # genus = "kosakonia"
    
        screen_name = genus + "_jobs"
    
        function_call = f"watchdog_boss(MAX_JOBS_AMOUNT={MAX_JOBS_AMOUNT})"
    
        with open(f"{screen_name}.sh", "w") as shell:
            shell.write(f"python3.6 -c 'from job_submitter import watchdog_boss; {function_call}'")
    
        #command = f"nohup python3.6 -c 'from job_submitter import watchdog_boss; {function_call}' &"
    
        command = f'screen -dmS {screen_name} bash -c "{screen_name}.sh; exec bash"'

        os.system(command)



def watchdog_boss(genus:str, MAX_JOBS_AMOUNT:int):
    # confirmation = "y"
    
    #genus = "kosakonia"
    
    # yes = confirmation == "y" or confirmation == "yes"
    
    # no = confirmation == "n" or confirmation == "no"
    
    MAX_JOBS_AMOUNT = int(MAX_JOBS_AMOUNT)
    
    # if no:
    #     print("halting...")
    #     sys.exit()
        
    # if yes:
        
    jobs_dir = os.getcwd()

    genus_batches_dir = f"{jobs_dir}/{genus}/batches"

    dir_content = os.listdir(genus_batches_dir)


    batch_pattern = f"{genus}_batch" + r"_[\d]{1,}.sh$"
    print(batch_pattern)

    batches = []

    for content in dir_content:
        batch = re.findall(batch_pattern, content)

        if len(batch) > 0:

            batches.append(batch[0])

    job_list = []

    for i in range(0, len(batches), MAX_JOBS_AMOUNT):
        job_list.append(batches[i:i + MAX_JOBS_AMOUNT])

    print(f"found {len(batches)} jobs, submitting in batches of {MAX_JOBS_AMOUNT}")

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
                    
            time.sleep(10*60)

    return True
    
    # else:
    #     os.system("kill %1")
    #     print("wrong input, please use y/n")
    #     input_manager()



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

    while(not watchdog(["first_LOG_feedback.txt", "second_LOG_feedback.txt", "third_LOG_feedback.txt"])):
        time.sleep(10)
        print("not yet")
    test2()


if __name__ == '__main__':
    main()
