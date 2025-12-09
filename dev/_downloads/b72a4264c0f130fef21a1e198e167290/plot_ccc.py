"""
Basic example on how to use the CCC cluster
===========================================

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

jobs = [
    executor.submit("sleep", k) for k in range(1, 11)
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


# %%
# Start Jobs
# ----------
#
# We can't execute the code on the CI since the CCC infrastructure is not
# available.

from hopla.config import Config

with Config(dryrun=True, delay_s=3):
    executor(max_jobs=2)
