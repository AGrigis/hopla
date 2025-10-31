##########################################################################
# NSAp - Copyright (C) CEA, 2022 - 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Configuration used by hopla.
"""

import contextvars

DEFAULT_OPTIONS = {
    "verbose": False,
    "dryrun": False,
    "delay_s": 60,
}

hopla_options = contextvars.ContextVar(
    "hopla_options",
    default=DEFAULT_OPTIONS,
)


class Config:
    """
    Context manager for modifying execution options passed to the
    :mod:`hopla.executor.Executor.__call__` method.

    Parameters
    ----------
    **options : dict
        Keyword arguments intercepted are:
        - verbose : bool, default False - print informations or not.
        - dryrun : bool, default False - execute commands or not.
        - delay_s : int, default 60 - refresh interval in seconds.

    Notes
    -----
    - The context variable `hopla_options` holds the current
      configuration.
    - Options are scoped to the `with` block and automatically restored
      afterward.
    """
    def __init__(self, **options):
        self.token = None
        self.options = options

    def __enter__(self):
        self.token = hopla_options.set(self.options)

    def __exit__(self, exc_type, exc_val, exc_tb):
        hopla_options.reset(self.token)
