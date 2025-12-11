"""
Basic example on how to use the CLI
===================================

Basic example

When you're running hundreds or thousands of jobs, automation is a necessity. 
This is where ``hopla`` can help you.

A simple example of how to use ``hopla`` on a cluster using the CLI interface.
Please check the :ref:`user guide <user_guide>` for a more in depth
presentation of all functionalities.
"""

import subprocess


command = ["hoplacli", "--config", "./examples/experiment.toml", "--njobs 2"]
subprocess.check_call(command)
