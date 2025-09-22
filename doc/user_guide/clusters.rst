.. _clusters:

Clusters
========

``hopla`` is preconfigured to operate with the NeuroSpin clusters. However,
adapting the code to suit your own infrastructure is possible.


PBS
---

Execution of 10 simple `sleep` commands.


.. code-block:: python

    import hopla
    from pprint import pprint

    executor = hopla.Executor(folder="/tmp/hopla", queue="Nspin_short",
                              walltime=1)

    jobs = [
        executor.submit("sleep", k) for k in range(1, 11)
    ]
    pprint(jobs)

    executor(max_jobs=2)
    print(executor.report)


.. tip::

    To execute a brainprep command available in an apptainer image, adapt and
    pass this command to the `executor.submit()` function:

    .. code-block:: bash

        apptainer run --bind <path> --cleanenv <image_path> brainprep <args>



CCC
---

Execution of 10 simple `sleep` commands available in an docker image.


.. code-block:: python

    import hopla
    from pprint import pprint

    executor = hopla.Executor(folder="/tmp/hopla", queue="rome",
                              walltime=1, project_id="genXXX",
                              image="/tmp/hopla/my-docker-img.tar")

    jobs = [
        executor.submit("sleep", k) for k in range(1, 11)
    ]
    pprint(jobs)

    executor(max_jobs=2)
    print(executor.report)


Execution of 10 simple `sleep` commands available in an docker image using a
multi tasks strategy (3 chunks here).


.. code-block:: python

    chunks = np.array_split(range(1, 11), 3)
    jobs = [
        executor.submit([hopla.DelayedSubmission("sleep", k) for k in c])
        for c in chunks
    ]


.. tip::

    You need to adapt the the `n_multi_cpus` parameter of the `Executor` in
    order to fit your need. Don't forget to check that your task fulfill the
    folowing core/memory ratios:
    
    - skylake parititon: 3.6G per core.
    - rome partition: 1.7G par core.

.. tip::

    To execution a brainprep command available in an docker image, adapt and
    pass this command to the `executor.submit()` function:

    .. code-block:: bash

        brainprep <args>

.. important::

    Don't forget to decalre the `n4h00001` hub by copying the 
    **.../n4h00001/n4h00001/config/repositories.yaml** file in your home directory
    **$HOME/.config/pcocc/repositories.yaml**.To list images don't forget
    also to export the **CCCWORKDIR** env variable to **n4h00001/n4h00001/gaia**.

.. important::

    Don't forget to load the **gcc/11.1.0** module to launch multi tasks jobs,
    and the **python3/3.12** (or another compatible version of Python) module.
    Dont't forget also to switch to the appropriate data
    **dfldatadir/XXX** module.

.. tip::

    You can export your docker image in a `.tar` file as follows:

    .. code-block:: bash

        docker save my-docker-img -o my-docker-img.tar 
