.. _cli:

CLI
===

``hopla`` has a CLI interface. The `hoplacli` command loads a TOML
configuration file, initializes a hopla executor, and submits jobs either
individually or in chunks depending on the configuration. It then runs the
executor with a specified maximum number of jobs and writes a report to disk.

.. code-block:: bash

    hoplacli --config ./examples/experiment.toml --njobs 2
