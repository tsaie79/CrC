import numpy as np
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

class CrC_scan_calc:
    def __init__(self):

        self.st_from_dir = "structures/c2cr3.vasp"
        self.st = Structure.from_file(self.st_from_dir)

        self.cr3c2 = Structure.from_file("structures/Cr3C2_tkid_23.vasp")
        self.cr23c6 = Structure.from_file("structures/Cr23C6_tkid_13.vasp")

        self.category = None

    def regular_wf(self):
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

    def test_encut(self):
        from atomate.vasp.fireworks import StaticFW
        from fireworks import Workflow
        from pymatgen.io.vasp.sets import MPScanStaticSet

        wfs = []
        self.category = "test_encut"
        for st, prev_tkid in zip([self.cr23c6], [13]):
            #        for st, prev_tkid in zip([self.cr3c2, self.cr23c6], [23, 13]):

            for encut in np.linspace(1000, 5000, 30):
                uis = {
                    "METAGGA": "Scan", "ENCUT": encut, "LCHARG": False, "LAECHG": False, "LELF": False,
                    "ISMEAR": 0, "SIGMA": 0.05,
                }
                scan_static_incar = MPScanStaticSet(st, bandgap=0.1, user_incar_settings=uis).incar
                scan_static_incar.pop("KSPACING")
                scan_static_incar.pop("MAGMOM")
                static_fw = StaticFW(st, vasp_input_set_params=dict(user_incar_settings=scan_static_incar))
                wf = Workflow([static_fw])
                wf.name = "{}-ENCUT{}".format(st.formula, encut)
                wf = set_queue_options(wf, "06:00:00")
                wf = preserve_fworker(wf)
                doc = {"category": self.category, "pc_from": prev_tkid, "test_set_date": "2021-11-12"}
                wf = add_additional_fields_to_taskdocs(wf, doc)
                wf = add_tags(wf, [doc])
                wf = set_execution_options(wf, category=self.category, fworker_name="owls")
                wf = add_modify_incar(wf)
                wfs.append(wf)
        return wfs

    @classmethod
    def run(cls):
        scan = cls()
        wfs = scan.test_encut()
        LPAD = LaunchPad.from_file(
            os.path.expanduser(os.path.join("~", "config/project/CrC/{}/"
                                                 "my_launchpad.yaml".format(scan.category))))
        for wf in wfs[:]:
            LPAD.add_wf(wf)

if __name__ == '__main__':
    print(os.getcwd())
    CrC_scan_calc.run()