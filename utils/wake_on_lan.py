import subprocess
import os


def wake_on_lan():
    cmd = ["wakeonlan", os.getenv("COMPUTER_MAC_ADDRESS")]
    subprocess.run(cmd)
