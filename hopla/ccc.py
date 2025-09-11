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

import copy
import json
import os
import shutil
import subprocess
import textwrap
import traceback
import warnings
from pathlib import Path

from .utils import DelayedJob, InfoWatcher, format_attributes


class CCCInfoWatcher(InfoWatcher):
    """ An instance of this class is shared by all jobs, and is in charge of
    calling ccc to check status for all jobs at once.

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
        return "squeue --states=all --json -j " + ",".join(active_jobs)

    @property
    def valid_status(self):
        """ Return the list of valid status.
        """
        return ["RUNNING", "PENDING", "SUSPENDED", "COMPLETING", "CONFIGURING",
                "UNKNOWN"]

    @classmethod
    def read_info(cls, string):
        """ Reads the output of squeue and returns a dictionary containing
        main jobs information.
        """
        if not isinstance(string, str):
            string = string.decode()
        all_stats = {str(val["job_id"]): val
                     for val in json.loads(string)["jobs"]}
        return all_stats


class DelayedCCCJob(DelayedJob):
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
    _hub = "n4h00001rs"
    _submission_cmd = "ccc_msub"

    def __init__(self, delayed_submission, executor, job_id):
        super().__init__(delayed_submission, executor, job_id)
        self.multi_task = isinstance(delayed_submission, (list, tuple))
        resource_dir = Path(__file__).parent / "resources"
        if self.multi_task:
            path = resource_dir / "ccc_multi_batch_template.txt"
            self.worker_file = resource_dir / "worker.sh"
        else:
            path = resource_dir / "ccc_batch_template.txt"
        with open(path) as of:
            self.template = of.read()
        image = self._executor.parameters["image"]
        assert image is not None, "Please select or give an image."
        if os.path.isfile(image):
            self.image_file = image
            self.image_name = os.path.basename(image).split(".tar")[0]
        else:
            self.image_file = None
            self.image_name = image

    # @property
    # def exitcode(self):
    #     """ Check if the code finished properly.
    #     """
    #     exitcode = True
    #     if self.paths.stdout.exists():
    #         exitcode = self._check_is_done(self.paths.stdout)
    #     if self.paths.stderr.exists():
    #         with open(self.paths.stderr) as of:
    #             content = [line.startswith("+ ") for line in of]
    #             exitcode = exitcode and all(content)
    #     return exitcode

    def generate_batch(self):
        """ Write the batch file.
        """
        params = copy.deepcopy(self._executor.parameters)
        params["walltime"] *= 3600
        params["memory"] *= 1000
        print(params["modules"])
        if params["modules"] != "":
            params["modules"] = f"module load {params['modules']}"
        try:
            self.import_image()
        except Exception:
            err = textwrap.indent(traceback.format_exc(), "   |")
            warnings.warn(
                f"Can't import image: {self.image_name}",
                stacklevel=2
            )
            print(err)
        if self.multi_task:
            n_multi_cpus = self._executor.parameters["nmulticpus"]
            shutil.copy(self.worker_file, self.paths.worker_file)
            # manage potentionl environment variables
            worker_env_insert = []
            pcocc_env_insert = ""
            if self._executor.parameters["ccc_envlist"] != []:
                for e in self._executor.parameters["ccc_envlist"]:
                    pcocc_env_insert += f"--env {e.split('=')[0]} "
                    worker_env_insert += [f'export {e}']
            with open(self.paths.worker_file, "r") as fp:
                tmp = fp.read()
            worker_env_insert = "\n" + "\n".join(worker_env_insert)
            tmp = tmp.replace('\n$@', f'{worker_env_insert}\n$@')
            with open(self.paths.worker_file, "w") as fp:
                fp.write(tmp)
            subcmds = [
                f"1-{n_multi_cpus} . {self.paths.worker_file} pcocc-rs run {pcocc_env_insert} "
                f"{self._hub}:{self.image_name} -- "
                f"{submission.command}"
                for submission in self.delayed_submission
            ]
            params["logdir"] = self.paths.flux_dir
            with open(self.paths.task_file, "w") as of:
                of.write("\n".join(subcmds))
            cmd = self.paths.task_file
        else:
            cmd = (
                f"pcocc-rs run {self._hub}:{self.image_name} "
                f"{self.delayed_submission.command}"
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
                **params))

    def import_image(self):
        """ Load the docker image if not available.
        """
        print("in the DelayedCCCJob>import image function")
        cmd = ["pcocc-rs", "image", "list", "-r", self._hub]
        stdout = subprocess.check_output(cmd)
        print(f'{self.image_name} should be in {self.read_index(stdout)}')
        if self.image_name not in self.read_index(stdout):
            if self.image_file is None:
                raise ValueError(
                    f"'{self.image_name}' image not available! Please "
                    "consider providing the image archive.")
            cmd = [
                "pcocc-rs", "image", "import",
                f"docker-archive:{self.image_file}",
                f"{self._hub}:{self.image_name}"]
            subprocess.check_call(cmd)

    @classmethod
    def read_index(cls, string):
        """ Reads the output of of pcocc-rs image list and returns a
        list available container.
        """
        if not isinstance(string, str):
            string = string.decode()
        names = [item.strip().split(" ")[0]
                 for item in string.split("\n")[2:-2]]
        return names

    def read_jobid(self, string):
        """ Return the started job ID.
        """
        if not isinstance(string, str):
            string = string.decode()
        return string.rstrip("\n").strip().split(" ")[-1]

    def sub_report(self):
        report = []
        prefix = f"{self.__class__.__name__}<job_id={self.job_id}>"
        if self.multi_task:
            log_files = list(self.paths.flux_dir.glob("bulk_*"))
            tasks_ids = [
                path.name.split("_")[1]
                for path in log_files
                if not self._check_is_done(path)
            ]
            report.append(
                f"{prefix}number_of_tasks: {len(self.delayed_submission)}")
            report.append(f"{prefix}failed_tasks: {tasks_ids}")
            report.append(f"{prefix}running_tasks: {len(log_files)}")
        return report

    @property
    def start_command(self):
        """ Return the start job command.
        """
        return type(self)._submission_cmd

    @property
    def stop_command(self):
        """ Return the stop job command.
        """
        return "ccc_mqdel"

    def __repr__(self):
        return format_attributes(
            self,
            attrs=["job_id", "submission_id", "_hub", "image_name"]
        )
