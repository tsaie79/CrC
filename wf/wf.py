from atomate.vasp.workflows import get_wf
from atomate.vasp.powerups import (
    add_additional_fields_to_taskdocs,
    preserve_fworker,
    add_modify_incar,
    set_queue_options,
    set_execution_options,
    clean_up_files,
    add_modify_kpoints,
    add_tags
)

from pymatgen import Structure

import os

from fireworks import LaunchPad

class ScanOpt:
    def __init__(self):
        self.st_from_dir = "../structures/Cr23C6_mp-723_primitive.cif"
        self.st = Structure.from_file(self.st_from_dir)
        self.category = None

    def test_set(self):
        self.category = "test_set"
        wf = get_wf(self.st, "metagga_optimization.yaml")
        wf = add_modify_incar(wf)
        wf = set_queue_options(wf, "24:00:00")
        wf = preserve_fworker(wf)
        doc = {"category": self.category, "pc_from": self.st_from_dir}
        wf = add_additional_fields_to_taskdocs(wf, doc)
        wf = add_tags(wf, [doc])
        wf = set_execution_options(wf, category=self.category, fworker_name="owls")
        print(wf)
        return wf

    @classmethod
    def run(cls):
        scan_opt = cls()
        wf = scan_opt.test_set()
        LPAD = LaunchPad.from_file(
            os.path.expanduser(os.path.join("~", "config/project/antisiteQubit/{}/"
                                                 "my_launchpad.yaml".format(scan_opt.category))))
        LPAD.add_wf(wf)
