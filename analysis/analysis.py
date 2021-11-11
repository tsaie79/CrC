import matplotlib.pyplot as plt
import pandas as pd

plt.style.use(['science', 'notebook', 'grid'])

from qubitPack.tool_box import get_db, IOTools

from pymatgen.electronic_structure.plotter import BSPlotter, DosPlotter, BSDOSPlotter

class ESPlotting:
    def __init__(self, dos_taskid=None, bs_taskid=None):
        self.db = get_db("CrC", "scan", port=1236)
        self.dos = self.db.get_dos(dos_taskid) if dos_taskid else None
        self.bs = self.db.get_band_structure(bs_taskid) if bs_taskid else None

    def total_dos(self):
        plotter = DosPlotter()
        plotter.add_dos("tdos", self.dos)
        plt = plotter.get_plot(xlim=[-5,5])
        plt.show()

    def projected_dos(self):
        plotter = DosPlotter()
        plotter.add_dos_dict(self.dos.get_element_dos())
        plt = plotter.get_plot(xlim=[-5, 5], ylim=[-50, 50])
        plt.show()

    def bandstructure(self):
        plotter = BSPlotter(self.bs)
        plt = plotter.get_plot()
        plt.show()


class EncutTesting:
    def __init__(self):
        self.db = get_db("CrC", "test_encut", port=12347)

        data = []
        for e in self.db.collection.find({"test_set_date": "2021-11-11"}):
            nsites = e["nsites"]
            formula = e["formula_pretty"]
            task_id = e["task_id"]
            encut = e["input"]["incar"]["ENCUT"]
            ismear = e["input"]["incar"]["ISMEAR"]
            sigma = e["input"]["incar"]["SIGMA"]
            energy = round(e["output"]["energy"], 3)

            data.append({"formula": formula, "encut": encut, "ismear": ismear, "sigma": sigma, "energy": energy,
                         "taskid": task_id, "nsites": nsites})
        self.data_df = pd.DataFrame(data)
        print(self.data_df["formula"].unique())
        self.data_gp = self.data_df.groupby(["formula", "ismear", "sigma", "encut", "taskid"]).aggregate({"energy": [
            "unique"]})
        print(self.data_gp)

    def energy_plt(self):
        formulas = self.data_df["formula"].unique()
        print(formulas)
        fig = plt.figure(figsize=(15, 15), dpi=300)
        for idx, formula in enumerate(formulas):
            ax = plt.subplot(2, 1, idx+1)
            ax.set_title(formula)

            df = self.data_df.loc[self.data_df["formula"] == formula, :]
            ismears = df["ismear"].unique()
            for ismear in ismears:
                # if formula == "Cr23C6":
                #     ismear_df = df.loc[(df["ismear"] == ismear) & (df["ismear"] != -5), :]
                # else:
                #     ismear_df = df.loc[(df["ismear"] == ismear), :]
                ismear_df = df.loc[df["ismear"] == ismear, :]
                sigmas = ismear_df["sigma"].unique()
                for sigma in sigmas:
                    sigma_df = ismear_df.loc[ismear_df["sigma"] == sigma, ["encut", "energy"]]
                    sigma_df = sigma_df.sort_values("encut")
                    sigma_df["dE per atom"] = sigma_df["energy"].diff()/sigma_df["nsites"].iloc[0]
                    ax.plot(sigma_df["encut"], sigma_df["energy"], "o--", label="ISMEAR={}-SIGMA={}".format(ismear,
                                                                                                             sigma))
                    ax.legend()
                    ax.set_xlabel("ENCUT (eV)")
                    ax.set_ylabel("Energy (eV)")


                    IOTools(cwd="analysis/output", pandas_df=sigma_df).to_excel("{}_{}_{}".format(formula, ismear,
                                                                                                 sigma))
                    print("**"*20)
                    print("formula:{} ismear:{} sigma:{}".format(formula, ismear, sigma))
                    print(ismear_df)
        fig.show()

if __name__ == '__main__':
    EncutTesting().energy_plt()