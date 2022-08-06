import abc

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

import latex
from util import stathelper


class Plot:
    def __init__(self, title, xlabel=None, ylabel=None):
        self.title = title
        self.fig, self.ax = plt.subplots()
        self.ax.set_title(self.title)
        if xlabel is not None:
            self.ax.set_xlabel(xlabel)
        if ylabel is not None:
            self.ax.set_ylabel(ylabel)
        self._prop_cycle = plt.rcParams['axes.prop_cycle']()  # we CALL the prop_cycle

    def renderizar(self, nombre_archivo=None, formato='pdf'):
        self.legend()
        if nombre_archivo is None:
            self.fig.show()
        else:
            # exportar figura, eliminando el espacio extra alrededor
            self.ax.set_title('')
            self.fig.savefig(latex.generated_img_path(f'{nombre_archivo}.{formato}', create_dirs=True), bbox_inches='tight')
            latex.write_figure_content_tex(nombre_archivo, self.title)

    def legend(self, loc='upper right'):
        if self.ax.get_legend_handles_labels() != ([], []):
            self.ax.legend(loc=loc)

    def plot(self, *args, **kwargs):
        return self.ax.plot(*args, **kwargs, **self._next_color(kwargs))

    def step(self, *args, **kwargs):
        return self.ax.step(*args, **kwargs, **self._next_color(kwargs))

    def hist(self, *args, **kwargs):
        return self.ax.hist(*args, **kwargs, **self._next_color(kwargs))

    def bar(self, *args, **kwargs):
        if 'yerr' in kwargs:
            if 'capsize' not in kwargs:
                kwargs['capsize'] = 80/len(args[0])
        return self.ax.bar(*args, **kwargs, **self._next_color(kwargs))

    def _next_color(self, kwargs):
        if 'color' in kwargs:
            return {}
        return next(self._prop_cycle)


class Grafico(Plot, abc.ABC):
    @abc.abstractmethod
    def graficar(self, *valores):
        pass


class GraficoContinuo(Grafico):
    def graficar(self, x, y, label=None):
        self.plot(x, y, label=label)


class GraficoDiscreto(Grafico):
    def graficar(self, x, y, label=None):
        self.step(x, y, label=label)


class GraficoDistribucion(Grafico):
    def __init__(self, title, xlabel=None, ylabel=None):
        if ylabel is None:
            ylabel = 'Frecuencia relativa'
        super().__init__(title, xlabel=xlabel, ylabel=ylabel)

    def graficar(self, valores, normal=True, marcar_valores=True, confianza=0.95):
        media, desvio = stathelper.mean(valores), stathelper.stdev(valores)
        if desvio != 0.0:
            self.hist(valores, bins='auto', density=True)
        else:  # desvío estándar == 0, todos los valores son iguales, no hay distribución normal ni IC
            self.bar(media, 1, width=0.2)
            # corregir rango, forzando desvío estándar = 1
            self.ax.set_xlim(*stats.norm(media).interval(.999))
        if normal:
            if desvio != 0.0:
                if len(valores) >= 30:  # al menos 30 elementos -> distribución normal
                    dist = stats.norm(loc=media, scale=desvio)
                else:  # menos de 30 elementos -> distribución t de Student
                    dist = stats.t(len(valores) - 1, loc=media, scale=desvio)
                x = np.linspace(dist.ppf(0.001), dist.ppf(0.999), 1000)
                pdf = dist.pdf(x)
                self.plot(x, pdf)
                if marcar_valores:
                    self.plot([dist.mean()] * 2, [0, pdf.max()], '--',
                              label='promedio estimado ($\\hat{\\mu}$)')
                    x1, x2 = dist.interval(confianza)
                    linea, = self.plot([x1] * 2, [0, dist.pdf(x1)], '--',
                                       label=f'IC {int(confianza * 100)}%')
                    self.plot([x2] * 2, [0, dist.pdf(x2)], '--', color=linea.get_color())
            else:
                if marcar_valores:
                    self.plot([media] * 2, [0, 1], '--',
                              label='promedio estimado ($\\hat{\\mu}$)')
