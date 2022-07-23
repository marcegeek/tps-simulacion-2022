import abc

import matplotlib.pyplot as plt
import numpy as np
import statistics as st
from scipy import stats


class Grafico(abc.ABC):
    def __init__(self, nombre, xlabel=None, ylabel=None):
        self.nombre = nombre
        self.fig, self.ax = plt.subplots()
        self.ax.set_title(self.nombre)
        if xlabel is not None:
            self.ax.set_xlabel(xlabel)
        if ylabel is not None:
            self.ax.set_ylabel(ylabel)

    @abc.abstractmethod
    def graficar(self, *valores):
        pass

    def renderizar(self):
        self.legend()
        self.fig.show()

    def legend(self):
        if self.ax.get_legend_handles_labels() != ([], []):
            self.ax.legend()


class GraficoContinuo(Grafico):
    def graficar(self, x, y, label=None):
        self.ax.plot(x, y, label=label)


class GraficoDiscreto(Grafico):
    def graficar(self, x, y, label=None):
        self.ax.step(x, y, label=label)


class GraficoDistribucion(Grafico):
    def __init__(self, nombre, xlabel=None, ylabel=None):
        if ylabel is None:
            ylabel = 'Frecuencia relativa'
        super().__init__(nombre, xlabel=xlabel, ylabel=ylabel)

    def graficar(self, valores, normal=True, marcar_valores=True, confianza=0.95):
        hist_y, _, _ = self.ax.hist(valores, bins='auto', density=True)
        if normal:
            dist = stats.norm(loc=st.mean(valores), scale=st.stdev(valores))
            x = np.linspace(dist.ppf(0.01), dist.ppf(0.99), 1000)
            pdf = dist.pdf(x)
            self.ax.plot(x, pdf)
            if marcar_valores:
                self.ax.plot([dist.mean()] * 2, [0, max(hist_y.max(), pdf.max()) * 1.05], '--',
                             label='promedio poblacional estimado ($\\hat{\\mu}$)')
                x1 = dist.ppf((1 - confianza) / 2)
                x2 = dist.ppf((1 + confianza) / 2)
                linea, = self.ax.plot([x1] * 2, [0, dist.pdf(x1)], '--',
                                      label=f'intervalo de confianza {int(confianza * 100)}%')
                self.ax.plot([x2] * 2, [0, dist.pdf(x2)], '--', color=linea.get_color())
