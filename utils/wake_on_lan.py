import subprocess
import os


def wake_on_lan():
    subprocess.run(os.getenv("WAKEONLAN_COMMAND"), shell=True)


def sleep_on_lan():
    subprocess.run(os.getenv("SLEEPONLAN_COMMAND"), shell=True)
