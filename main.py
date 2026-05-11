"""The main file of the robot which will install all requirements in
a virtual environment and then start the actual process.
"""

import subprocess
import os
import sys

script_directory = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_directory)

subprocess.run("pip install --upgrade uv", check=True)
command_args = ["uv", "run", "python", "-m", "afskrivining_af_foraeldede_sagsomkostninger"] + sys.argv[1:]
subprocess.run(command_args, check=True)
