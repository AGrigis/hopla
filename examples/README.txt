.. _sphx_glr_auto_gallery:

Usage Examples
==============

From within an environment with hopla installed, you can seamlessly connect
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


How It Works
------------

- **Executor Context**: The `Executor` context manages all cluster
  configurations and task execution.

- **Submit a Job**: The function `executor.submit()` configure as a delayed
  job to the Executor.

- **Start the Job**: You can either start the job manually or have it
  automatically executed when executor() is called. You can control
  concurrency by setting `max_jobs` to limit the number of tasks running
  simultaneously.

- **Execution Reporting**: Once the job completes, the result is retrieved in
  the `executor.reprot`.

PBS cluster
-----------

Execution of a simple `sleep` command::

    import hopla
    from pprint import pprint

    executor = hopla.Executor(folder="/tmp/hopla", queue="Nspin_short",
                              walltime=1)

    jobs = [executor.submit("sleep", k) for k in range(1, 11)]
    pprint(jobs)

    executor(max_jobs=2)
    print(executor.report)

Execution of a brainprep command available in an apptainer image (adapt and
pass this command to the `executor.submit()` function)::

    apptainer run --bind <path> --cleanenv <image_path> brainprep <args>


CCC cluster
-----------

Execution of a simple `sleep` command available in an docker image::

    import hopla
    from pprint import pprint

    executor = hopla.Executor(folder="/tmp/hopla", queue="rome",
                              walltime=1, project_id="genXXX",
                              image="/tmp/hopla/my-docker-img.tar")

    jobs = [executor.submit("sleep", k) for k in range(1, 11)]
    pprint(jobs)

    executor(max_jobs=2)
    print(executor.report)


Execution of a brainprep command available in an docker image (adapt and
pass this command to the `executor.submit()` function)::

    brainprep <args>

Don't forget to set decalre the `n4h00001` hub by copying the 
`n4h00001/n4h00001/config/repositories.yaml` file in your home directory
`$HOME/.config/pcocc/repositories.yaml`.


Docker
------

You can't export your docker image as follows::

    docker save my-docker-img -o my-docker-img.tar 


.. contents:: **Contents**
    :local:
    :depth: 1

