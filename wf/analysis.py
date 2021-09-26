from qubitPack.tool_box import get_db

from pymatgen.electronic_structure.plotter import BSPlotter, DosPlotter, BSDOSPlotter

class Plotting:
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

if __name__ == '__main__':
    plt = Plotting(24)
    plt.projected_dos()