import abc
import statistics

import numpy as np
import matplotlib.pyplot as plt
import statistics as st

from util.plotter import GraficoDistribucion


class Evento:
    """Clase base evento con callback para la rutina correspondiente"""

    def __init__(self, tiempo, callback):
        self.tiempo = tiempo
        self.callback = callback

    def __lt__(self, other):
        return self.tiempo < other.tiempo

    def __gt__(self, other):
        return self.tiempo > other.tiempo

    def manejar(self):
        self.callback(self)


class Simulacion(abc.ABC):
    """Clase base de una simulación por eventos discretos"""

    def __init__(self, semilla=None):
        self.reloj = 0.
        self.eventos = []
        self.sig_evento = None  # el valor se modifica en la rutina de avance en el tiempo
        self.tiempo_ult_evento = 0.
        self.tiempo_desde_ult_evento = 0.
        self.np_randomstate = np.random.RandomState(semilla)

    def avance_tiempo(self):
        if len(self.eventos) == 0:
            print(f'Lista de eventos vacía en el tiempo {self.reloj}')
            raise Exception('Lista de eventos vacía')
        self.sig_evento = min(self.eventos)
        self.reloj = self.sig_evento.tiempo

    def actualizar_estadisticas(self):
        self.tiempo_desde_ult_evento = self.reloj - self.tiempo_ult_evento
        self.tiempo_ult_evento = self.reloj

    def hacer_un_paso(self):
        self.avance_tiempo()
        self.actualizar_estadisticas()
        self.sig_evento.manejar()
        self.eventos.remove(self.sig_evento)
        self.sig_evento = None

    @abc.abstractmethod
    def es_fin(self):
        pass

    def correr(self, mostrar=False):
        """Relizar una corrida de la simulación"""
        while not self.es_fin():
            self.hacer_un_paso()
        if mostrar:
            self.informe()

    @abc.abstractmethod
    def informe(self):
        pass

    @classmethod
    @abc.abstractmethod
    def medidas_estadisticas(cls):
        """
        Devuelve diccionario con los nombres de cada estadístico y su método como tupla, la clave representa
        el nombre con el que se va a exportar la gráfica respectiva.
        Formato: {'clave': ('nombre estadístico o título de gráfica', cls.metodo), ...}
        """
        pass


class Experimento:
    """Realizar un experimento con varias corridas de una simulación"""

    def __init__(self, clase, params, param_kwargs, corridas=10):
        self._clase = clase
        self.resultados = [self._clase(*params, **param_kwargs) for i in range(corridas)]

    def correr(self):
        for s in self.resultados:
            s.correr()

    def reportar(self, exportar=False, mostrar=True):
        idx = np.random.randint(0, len(self.resultados) - 1)
        print(f'Resultados corrida n° {idx + 1} (seleccionada al azar):')
        self.resultados[idx].informe()
        diccionario_medidas = self._clase.medidas_estadisticas()
        distribuciones = {}
        for k in diccionario_medidas:
            distribuciones[k] = []
        for sim in self.resultados:
            for k in diccionario_medidas:
                # el método está tomado desde la clase, así que sacamos el nombre y bajamos a la instancia
                nombre_metodo = diccionario_medidas[k][1].__name__
                metodo = getattr(sim, nombre_metodo)
                distribuciones[k].append(metodo())
        print()
        print(f'Resultados experimento:')
        print(f'Corridas: {len(self.resultados)}')
        for k in distribuciones:
            promedio_promedios = statistics.mean(distribuciones[k])
            desvio_promedios = statistics.stdev(distribuciones[k])
            print(f'{diccionario_medidas[k][0]}: promedio de promedios: {promedio_promedios}, desvío estándar: {desvio_promedios}')
            graf = GraficoDistribucion(diccionario_medidas[k][0])
            graf.graficar(distribuciones[k])
            graf.legend()
            if exportar:
                #graf.renderizar()  TODO hacer exportación
                pass
        if mostrar:
            plt.show()
