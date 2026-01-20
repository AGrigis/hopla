.. _cli:

CLI
===

`hoplacli` is a command-line interface designed to automate job submission and
execution using the ``hopla`` framework.
It loads a TOML configuration file, prepares an execution environment, submits
jobs (individually or in chunks), and produces a final execution report.
This guide explains how to use the CLI, how to structure the TOML
configuration file, and how the workflow operates.

Usage
-----

.. code-block:: bash

    hoplacli --config --config <config_file.toml> --njobs <N>

An ``experiment.toml`` demonstration configuration file can be found in the
project examples folder.

Workflow
--------

1. Parse CLI arguments using ``argparse``.
2. Load the TOML configuration file with ``tomllib``: expect four mandatory
   sections (``[project]``, ``[inputs]``, ``[environment]``, and ``[config]``)
   and one optional (``[multi]``).
3. Initialize a `:class:`~hopla.executor.Executor`` with ``[environment]``
   settings.
4. Extract and submit commands from the ``[inputs]`` settings:
   - If a ``[multi]`` section is present, split commands into chunks and
     submit them as delayed submissions.
   - Otherwise, submit commands directly.
5. Run the executor with the specified maximum number of jobs using the
   ``[config]`` settings.
6. Write a textual report to ``report.txt`` inside the executor's working
   directory.

TOML Configuration
------------------

The configuration file is divided into several sections.

``[project]``
~~~~~~~~~~~~~

``name`` (str)
    Project name.

``operator`` (str)
    Person responsible for running the analysis.

``date`` (str)
    Date of the experiment in ``DD/MM/YYYY`` format.

``[inputs]``
~~~~~~~~~~~~

``commands`` (str or list)
    Commands to execute. May be a Python expression string (e.g.
    ``"sleep {k}"``) or a list of explicit commands.

``parameters`` (str)
    Additional parameters passed to the container execution command
    (e.g. ``"--cleanenv"``).

``[environment]``
~~~~~~~~~~~~~~~~~

See the :class:`~hopla.executor.Executor` parameters.

``[config]``
~~~~~~~~~~~~

``dryrun`` (bool)
    Simulate job submission without executing.

``delay_s`` (int)
    Delay (seconds) between submissions.

``verbose`` (bool)
    Enable verbose logging.

``[multi]`` (optional)
~~~~~~~~~~~~~~~~~~~~~~

``n_splits`` (int)
    Number of chunks to split commands into.

Notes
-----

- The ``multi`` section is optional but required for chunked submissions.
- The ``Config`` context manager is used internally to apply configuration
  settings during execution.
