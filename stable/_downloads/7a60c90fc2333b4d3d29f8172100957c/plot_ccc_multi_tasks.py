"""
Basic example on how to use the CCC cluster using multi-tasks
=============================================================

Basic example

When you're running hundreds or thousands of jobs, automation is a necessity. 
This is where ``hopla`` can help you.

A simple example of how to use ``hopla`` on a CCC cluster. Please check
the :ref:`user guide <user_guide>` for a more in depth presentation of all
functionalities.


Imports
-------
"""

import hopla
import numpy as np
from pprint import pprint


# %%
# Executor Context
# ----------------

executor = hopla.Executor(
    cluster="ccc",
    folder="/tmp/hopla",
    queue="rome",
    image="/tmp/hopla/my-docker-img.tar",
    walltime=1,
    project_id="genXXX",
)


# %%
# Submit Jobs
# -----------

chunks = np.array_split(range(1, 11), 3)
jobs = [
    executor.submit([hopla.DelayedSubmission("sleep", k) for k in c])
    for c in chunks
]
pprint(jobs)
print(jobs[0].delayed_submission)


# %%
# Generate a batch
# ----------------

jobs[0].generate_batch()
print(jobs[0].paths)
batch = jobs[0].paths.submission_file
with open(batch) as of:
    print(of.read())
tasks = jobs[0].paths.task_file
with open(tasks) as of:
    print(of.read())


# %%
# Start Jobs
# ----------
#
# We can't execute the code on the CI since the CCC infrastructure is not
# available.

from hopla.config import Config

with Config(dryrun=True, delay_s=3):
    executor(max_jobs=2)
