##########################################################################
# Hopla - Copyright (C) AGrigis, 2015 - 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

import argparse

import numpy as np
import pandas as pd
import tomllib

import hopla
from hopla.config import Config


def main():
    """
    Command-line interface for automated job execution with hopla.

    This function parses command-line arguments, loads a TOML configuration
    file, initializes a hopla executor, and submits jobs either individually
    or in chunks depending on the configuration. It then runs the executor
    with a specified maximum number of jobs and writes a report to disk.

    Workflow
    --------
    1. Parse CLI arguments using argparse.
    2. Load the TOML configuration file with `tomllib`.
    3. Initialize a `hopla.Executor` with environment parameters.
    4. Extract commands from the configuration:
       - If `multi` is defined, split commands into chunks and submit them
         as delayed submissions.
       - Otherwise, submit commands directly.
    5. Run the executor with the specified maximum number of jobs.
    6. Write a textual report to `report.txt` inside the executor's folder.

    TOML Configuration
    ------------------
    The configuration file is structured into sections:

    [project]
    name : str
        Name of the project.
    operator : str
        Person responsible for running the analysis.
    date : str
        Date of the experiment in DD/MM/YYYY format.

    [inputs]
    commands : str or list
        Commands to execute. Can be a Python expression string (e.g.,
        "sleep {k}") or a list of commands.
    data : str
        A TSV file used to fill the previous Python expression string.
        Column names must match expression (e.g., "k" in the previous
        example).
    parameters : str
        Additional parameters passed to the container execution command
        (e.g., "--cleanenv").

    [environment]
    cluster : str
        Cluster type (e.g., "pbs").
    folder : str
        Working directory for job execution (e.g., "/tmp/hopla").
    queue : str
        Queue or partition name (e.g., "Nspin_short").
    walltime : int
        Maximum walltime in hours for each job.
    n_cpus : int
        Number of CPUs allocated per job.
    image : str
        Path to container image used for execution.

    [config]
    dryrun : bool
        If true, simulate job submission without executing.
    delay_s : int
        Delay in seconds between submissions.
    verbose : bool
        If true, enable verbose logging.

    Examples
    --------
    >>> hoplactl --config experiment.toml --njobs 5 # doctest: +SKIP

    Notes
    -----
    - The `multi` section should define `n_splits` to control chunking.
    - The `Config` context manager is used to apply configuration settings
      during execution.
    """
    parser = argparse.ArgumentParser(
        prog="hoplactl",
        description=(
            "Automate job execution with hopla using a configuration file.\n\n"
            "This function parses command-line arguments, loads a TOML "
            "configuration file, initializes a hopla executor, and submits "
            "jobs either individually or in chunks depending on the "
            "configuration. It then runs the executor with a specified "
            "maximum number of jobs and writes a report to disk."
        ),
        epilog="Notes:\n- Use a valid TOML file.\n- See docs for examples.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--config",
        type=str,
        required=True,
        help=(
            "Path to an experiment TOML configuration file. The file must "
            "contain sections for `project`, `environment`, `inputs`, and "
            "`config`. Optionally, a `multi` section can be provided to split "
            "commands into chunks."
        )
    )
    parser.add_argument(
        "--njobs",
        type=int,
        required=True,
        help="The maximum number of job submissions to execute concurrently."
    )
    args = parser.parse_args()

    with open(args.config, "rb") as of:
        config = tomllib.load(of)

    executor = hopla.Executor(
        **config["environment"]
    )

    commands = config["inputs"]["commands"]
    if not isinstance(commands, (list, tuple)):
        df = pd.read_csv(config["inputs"]["data"], sep="\t")
        commands = [commands.format(**dict(row)) for _, row in df.iterrows()]
    if config.get("multi") is not None:
        chunks = np.array_split(commands, config["multi"]["n_splits"])
        jobs = [
            executor.submit(
                [hopla.DelayedSubmission(cmd) for cmd in subcmds],
                execution_parameters=config["inputs"].get("parameters"),
            ) for subcmds in chunks
        ]
    else:
        jobs = [
            executor.submit(
                cmd,
                execution_parameters=config["inputs"].get("parameters"),
            ) for cmd in commands
        ]
    print(jobs)

    with Config(**config["config"]):
        executor(max_jobs=args.njobs)

    report_file = executor.folder / "report.txt"
    with open(report_file, "w") as of:
        of.write(executor.report)


if __name__ == "__main__":
    main()
