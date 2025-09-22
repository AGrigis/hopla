##########################################################################
# Hopla - Copyright (C) AGrigis, 2015 - 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Contains some utility functions.
"""

import shutil
import subprocess
import textwrap
import time
import warnings
from abc import ABC, abstractmethod


def format_attributes(cls, attrs=None):
    """ Automatically format class attributes.

    Parameters
    ----------
    cls: object
        an input class.
    attrs: list of str, default None
        the attributes to add in the final description.

    Returns
    -------
    repr: str
        the class representation.
    """
    attrs = attrs or dir(cls)
    attributes = textwrap.indent(
        "\n".join([
            f"{attr}={getattr(cls, attr)}," for attr in attrs
            if not attr.startswith("__")
        ]),
        "  "
    )
    return f"{cls.__class__.__name__}(\n{attributes}\n)"


class JobPaths:
    """ Creates paths related to a job and its submission.

    Parameters
    ----------
    folder: Path
        the current execution folder.
    job_id: str
        the job identifier.
    """
    def __init__(self, folder, job_id):
        self.submission_folder = folder / "submissions"
        self.log_folder = folder / "logs"
        if self.submission_folder.exists():
            shutil.rmtree(self.submission_folder)
        if self.log_folder.exists():
            shutil.rmtree(self.log_folder)
        self.submission_folder.mkdir(parents=True, exist_ok=True)
        self.log_folder.mkdir(parents=True, exist_ok=True)
        self.job_id = job_id

    @property
    def submission_file(self):
        """ Generate the submission file location.
        """
        return self.submission_folder / f"{self.job_id}_submission.sh"

    @property
    def stderr(self):
        """ Generate the stderr file location.
        """
        return self.log_folder / f"{self.job_id}_log.err"

    @property
    def stdout(self):
        """ Generate the stdout file location.
        """
        return self.log_folder / f"{self.job_id}_log.out"

    @property
    def task_file(self):
        """ Generate the task file location.
        """
        return self.submission_folder / f"{self.job_id}_tasks.txt"

    @property
    def worker_file(self):
        """ Generate the worker file location.
        """
        return self.submission_folder / "worker.sh"

    @property
    def flux_dir(self):
        """ Generate the flux output dir.
        """
        path = self.log_folder / f"{self.job_id}_flux"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def __repr__(self):
        return format_attributes(self)


class InfoWatcher(ABC):
    """ An instance of this class is shared by all jobs, and is in charge of
    calling scheduler to check status for all jobs at once.

    Parameters
    ----------
    delay_s: int, default 60
        maximum delay before each non-forced call to the cluster.
    """
    def __init__(self, delay_s=60):
        self._delay_s = delay_s
        self._last_status_check = time.time()
        self._output = b""
        self._num_calls = 0
        self._info_dict = {}
        self._registered = set()
        self._finished = set()

    def clear(self):
        """ Clears cache.
        """
        self._last_status_check = time.time()
        self._output = b""
        self._num_calls = 0
        self._info_dict = {}
        self._registered = set()
        self._finished = set()

    def get_info(self, job_id):
        """ Returns a dict containing info about the job.

        Parameters
        ----------
        job_id: int
            id of the job on the cluster.
        """
        if job_id not in self._registered:
            self.register_job(job_id)
        last_check_delta = time.time() - self._last_status_check
        if last_check_delta > self._delay_s:
            self.update()
        return self._info_dict.get(job_id, {})

    def get_state(self, job_id):
        """ Returns the state of the job.

        Parameters
        ----------
        job_id: str
            id of the job on the cluster.
        """
        info = self.get_info(job_id)
        state = info.get("job_state") or "UNKNOWN"
        if isinstance(state, (list, tuple)):
            state = state[-1]
        return state

    def register_job(self, job_id):
        """ Register a job on the instance for shared update.
        """
        assert isinstance(job_id, str), f"{job_id} - {type(job_id)}"
        self._registered.add(job_id)

    def update(self):
        """ Updates the info of all registered jobs.
        """
        if len(self._registered) == 0:
            return
        self._num_calls += 1
        try:
            self._output = subprocess.check_output(
                self.update_command, shell=True)
        except Exception as e:
            warnings.warn(
                f"Call #{self._num_calls} - Bypassing qstat error {e}, status "
                "may be inaccurate.", stacklevel=2
            )
        else:
            self._info_dict.update(self.read_info(self._output))
        self._last_status_check = time.time()
        active_jobs = self._registered - self._finished
        for job_id in active_jobs:
            if self.is_done(job_id):
                self._finished.add(job_id)

    def is_done(self, job_id):
        """ Returns whether the job is finished.

        Parameters
        ----------
        job_id: str
            id of the job on the cluster.
        """
        state = self.get_state(job_id)
        return state.upper() not in self.valid_status

    @property
    @abstractmethod
    def update_command(self):
        """ Return the command to list jobs status.
        """

    @property
    @abstractmethod
    def valid_status(self):
        """ Return the list of valid status.
        """

    @abstractmethod
    def read_info(self, string):
        """ Reads the output of the update command and returns a dictionary
        containing main jobs information.
        """


class DelayedJob(ABC):
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
    def __init__(self, delayed_submission, executor, job_id):
        self.delayed_submission = delayed_submission
        self._executor = executor
        self.job_id = job_id
        self.submission_id = None
        self.stderr = None
        self.paths = JobPaths(self._executor.folder, self.job_id)

    @property
    def done(self):
        """ Checks whether the job is finished properly.
        """
        if self.submission_id is None:
            return False
        if self.submission_id == "EXIT":
            return True
        return self._executor.watcher.is_done(self.submission_id)

    @property
    def status(self):
        """ Checks the job status.
        """
        if self.submission_id is None:
            return "NOTSTARTED"
        return self._executor.watcher.get_state(self.submission_id)

    @property
    def exitcode(self):
        """ Check if the code finished properly.
        """
        if self.paths.stdout.exists():
            return self._check_is_done(self.paths.stdout)
        return False

    @classmethod
    def _check_is_done(cls, path):
        """ Check if the input file finished by done.
        """
        with open(path) as of:
            content = of.read().split("##########")[0].strip("\n")
        return "HOPLASAY-DONE" in content.split("\n")

    def _register_in_watcher(self):
        self._executor.watcher.register_job(self.submission_id)

    @property
    def report(self):
        """ Generate a report for the submitted job.
        """
        message = ["-" * 40]
        code = "success" if self.exitcode else "failure"
        prefix = f"{self.__class__.__name__}<job_id={self.job_id}>"
        message.append(f"{prefix}exitcode: {code}")
        if self.paths.submission_file.exists():
            message.append(f"{prefix}submission: {self.paths.submission_file}")
        else:
            message.append(f"{prefix}submission: none")
        if self.paths.stdout.exists():
            message.append(f"{prefix}stdout: {self.paths.stdout}")
            with open(self.paths.stdout) as of:
                info = [line.strip("\n") for line in of]
            message.append(f"{prefix}submission_id: {info[0]}")
            message.append(f"{prefix}node: {info[1]}")
        else:
            message.append(f"{prefix}stdout: none")
        if self.paths.stderr.exists():
            message.append(f"<{prefix}stderr: {self.paths.stderr}")
        elif self.stderr is not None:
            message.append(f"<{prefix}stderr: {self.stderr}")
        else:
            message.append(f"{prefix}stderr: none")
        message.extend(self.sub_report())
        return "\n".join(message)

    def sub_report(self):
        """ Overload this method to extend the final report.
        """
        return []

    def start(self):
        """ Start a job.
        """
        self.generate_batch()
        if self.submission_id is None or self.done:
            process = subprocess.Popen(
                [self.start_command, self.paths.submission_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            self.submission_id = self.read_jobid(stdout)
            if not self.submission_id.isdigit():
                self.submission_id = "EXIT"
                self.stderr = stderr.decode("utf8")
            # print(f"Job {self.submission_id} - {self.paths.submission_file} "
            #        "is running!")
            self._register_in_watcher()

    def stop(self):
        """ Stop a job.
        """
        if self.submission_id is not None or not self.done:
            cmd = [self.stop_command, self.job_id]
            subprocess.check_call(cmd)

    @abstractmethod
    def read_jobid(self, string):
        """ Return the started job ID.
        """

    @abstractmethod
    def generate_batch(self):
        """ Write the batch file.
        """

    @property
    @abstractmethod
    def start_command(self):
        """ Return the start job command.
        """

    @property
    @abstractmethod
    def stop_command(self):
        """ Return the stop job command.
        """
