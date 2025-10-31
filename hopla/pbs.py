##########################################################################
# Hopla - Copyright (C) AGrigis, 2015 - 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Contains PBS specific functions.
"""

import json
import os
from pathlib import Path

from .utils import DelayedJob, InfoWatcher, format_attributes


class PbsInfoWatcher(InfoWatcher):
    """ An instance of this class is shared by all jobs, and is in charge of
    calling pbs to check status for all jobs at once.

    Parameters
    ----------
    delay_s: int, default 60
        maximum delay before each non-forced call to the cluster.
    """
    def __init__(self, delay_s=60):
        super().__init__(delay_s)

    @property
    def update_command(self):
        """ Return the command to list jobs status.
        """
        active_jobs = self._registered - self._finished
        print(self._registered, self._finished)
        return "qstat -fx -F json " + " ".join(active_jobs)

    @property
    def valid_status(self):
        """ Return the list of valid status.
        """
        return ["R", "Q", "S", "UNKNOWN"]

    @classmethod
    def read_info(cls, string):
        """ Reads the output of qstat and returns a dictionary containing
        main jobs information.
        """
        if not isinstance(string, str):
            string = string.decode()
        all_stats = {key.split(".")[0]: val
                     for key, val in json.loads(string)["Jobs"].items()}
        return all_stats


class DelayedPbsJob(DelayedJob):
    """ Represents a job that have been queue for submission by an executor,
    but hasn't yet been scheduled.

    Parameters
    ----------
    delayed_submission: DelayedSubmission
        a delayed submission allowing to generate the command line to
        execute.
    executor: Executor
        base job executor.
    job_id: str
        the job identifier.
    """
    _submission_cmd = "qsub"
    _container_cmd = "apptainer run {params} {image_path} {command}"

    def __init__(self, delayed_submission, executor, job_id):
        super().__init__(delayed_submission, executor, job_id)
        resource_dir = Path(__file__).parent / "resources"
        path = resource_dir / "pbs_batch_template.txt"
        with open(path) as of:
            self.template = of.read()
        self.image_path = self._executor.parameters["image"]

    def generate_batch(self):
        """ Write the batch file.
        """
        cmd = self._container_cmd.format(
            image_path=self.image_path,
            params=self.delayed_submission.execution_parameters,
            command=self.delayed_submission.command
        )
        with open(self.paths.submission_file, "w") as of:
            if self.paths.stdout.exists():
                os.remove(self.paths.stdout)
            if self.paths.stderr.exists():
                os.remove(self.paths.stderr)
            of.write(self.template.format(
                command=cmd,
                stdout=self.paths.stdout,
                stderr=self.paths.stderr,
                **self._executor.parameters))

    def read_jobid(self, string):
        """ Return the started job ID.
        """
        if not isinstance(string, str):
            string = string.decode()
        return string.rstrip("\n").split(".")[0]

    @property
    def start_command(self):
        """ Return the start job command.
        """
        return type(self)._submission_cmd

    @property
    def stop_command(self):
        """ Return the stop job command.
        """
        return "qdel"

    def __repr__(self):
        return format_attributes(
            self,
            attrs=["job_id", "submission_id"]
        )
