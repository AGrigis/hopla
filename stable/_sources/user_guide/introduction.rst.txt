.. _introduction:

Introduction
============

From within an environment with ``hopla`` installed, you can seamlessly connect
to a cluster, configure nodes, and deploy applications while managing
resources and scaling workloads by running dynamic scripts. The execution
pipeline is as follows:

- **Cluster Configuration**: All cluster settings are stored within the 
  Executor context manager, ensuring a centralized and consistent
  configuration.

- **Job Submission**: The Executor context manager enables you to submit
  delayed jobs, allowing for deferred execution based on resource
  availability and job priorities.

- **Start the Job**: You can manually start and stop these jobs, or leverage
  the Executor context manager to automatically launch them, controlling
  the number of jobs running concurrently to optimize resource utilization.

- **Execution Reporting**: Finally, the Executor context manager provides
  an execution report, offering insights into the status, performance, and
  resource usage of each job executed within the cluster.

``hopla`` is designed to run embarrassingly parallel jobs, i.e. independent
processes in parallel using containers.

.. note::

    Jobs need no communication.
