import time
import os
import re

def test_function():
    print(os.getcwd())

    time.sleep(1*60)

    os.system("touch first_LOG.txt")

    time.sleep(2*60)

    os.system("touch second_LOG.txt")

    time.sleep(3*60)

    os.system("touch third_LOG.txt")


def test2():
    print("ALL DONE")


def watchdog(job_names):
    fir_content = os.listdir()

    print(fir_content)

    all_done = True

    for job in job_names:
        if not job in fir_content:
            print(f"{job} not yet done")
            all_done = False

    return all_done


def main():

    while(not watchdog(["first_LOG.txt", "second_LOG.txt", "third_LOG.txt"])):
        time.sleep(10)
        print("not yet")
    test2()


if __name__ == '__main__':
    main()
