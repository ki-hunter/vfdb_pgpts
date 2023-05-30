import os
import time

print(os.getcwd())
dir = os.getcwd()
time.sleep(1*60)

os.system(f"touch {dir}/first_LOG.txt")

time.sleep(1*60)

os.system(f"touch {dir}/second_LOG.txt")

time.sleep(1*60)

os.system(f"touch {dir}/third_LOG.txt")