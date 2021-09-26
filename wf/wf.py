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

from pymatgen.io.vasp.inputs import Structure

import os

from fireworks import LaunchPad

# from qubitPack.tool_box import get_db

class ScanOpt:
    def __init__(self):

        self.st_from_dir = "structures/c2cr3.vasp"
        self.st = Structure.from_file(self.st_from_dir)

        # db = get_db("CrC", "test_set", port=12347)
        # st = db.collection.find_one({"task_id": 9})["output"]["structure"]
        # self.st = Structure.from_dict(st)
        self.category = None

    def test_set(self):
        self.category = "scan"
        wf = get_wf(self.st, os.path.join(os.path.dirname(os.path.abspath("__file__")),
                                          "wf/metagga_optimization.yaml"))
        wf = add_modify_incar(wf, dict(incar_update={"EDIFFG": -0.04}), fw_name_constraint=wf.fws[0].name)
        wf = add_modify_incar(wf, dict(incar_update={"EDIFFG": -0.01}), fw_name_constraint=wf.fws[1].name)
        wf = add_modify_incar(wf, dict(incar_update={"LAECHG": False, "LELF": False, "ISPIN": 2, "METAGGA": "SCAN"}))
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
            os.path.expanduser(os.path.join("~", "config/project/CrC/{}/"
                                                 "my_launchpad.yaml".format(scan_opt.category))))
        LPAD.add_wf(wf)

if __name__ == '__main__':
    print(os.getcwd())
    ScanOpt.run()