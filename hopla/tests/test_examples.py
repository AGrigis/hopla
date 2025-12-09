##########################################################################
# NSAp - Copyright (C) CEA, 2021 - 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################


import unittest
import runpy
from pathlib import Path


class TestGalleryExamples(unittest.TestCase):

    def setUp(self):
        self.examples_dir = Path(__file__).parent.parent.parent / "examples"

    def test_pbs(self):
        script_path = self.examples_dir / "plot_pbs.py"
        runpy.run_path(str(script_path))

    def test_slurm(self):
        script_path = self.examples_dir / "plot_slurm.py"
        runpy.run_path(str(script_path))

    def test_ccc(self):
        script_path = self.examples_dir / "plot_ccc.py"
        runpy.run_path(str(script_path))

    def test_ccc_multi_tasks(self):
        script_path = self.examples_dir / "plot_ccc_multi_tasks.py"
        runpy.run_path(str(script_path))


if __name__ == "__main__":
    unittest.main()
