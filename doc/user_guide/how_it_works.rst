.. _how_it_works:

How It Works
============

- **Executor Context**: The :class:`~hopla.executor.Executor` context manages
  all cluster configurations and task execution.

- **Submit a Job**: The method :meth:`~hopla.executor.Executor.submit()`
  configure a delayed job to the :class:`~hopla.executor.Executor`. 

- **Start the Job**: You can either start the job manually with the
  :meth:`~hopla.utils.DelayedJob.start()` method attached or call the
  :class:`~hopla.executor.Executor` instance to run all jobs. With the last
  method, you can control concurrency by setting `max_jobs` to limit the
  number of tasks running simultaneously. Note that it is possible to only
  generate the batch file associated to a job using the
  :meth:`~hopla.utils.DelayedJob.generate_batch()` method.

- **Execution Reporting**: Once the job completes, the result is retrieved in
  the :class:`~hopla.executor.Executor` instance `report` property.
