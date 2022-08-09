import abc
import itertools

import numpy as np
import matplotlib.pyplot as plt

from util import stathelper

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterator, *args, **kwargs):
        return iterator

from util.plotter import Plot, GraficoDistribucion, GraficoDiscreto


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

    # noinspection PyPep8Naming,PyPropertyDefinition
    @staticmethod
    @property
    @abc.abstractmethod
    def NOMBRE_MODELO():
        pass

    # noinspection PyPep8Naming,PyPropertyDefinition
    @staticmethod
    @property
    @abc.abstractmethod
    def CLAVE():
        pass

    def __init__(self, semilla=None):
        self.reloj = 0.
        self.tiempos = [self.reloj]
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
        self.tiempos.append(self.reloj)

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

    @abc.abstractmethod
    def medidas_estadisticas(self):
        """
        Devuelve diccionario con las variables estadísticas correspondientes (VariableEstadistica), la clave representa
        el nombre con el que se va a exportar la gráfica respectiva.
        Formato: {'clave': VariableEstadistica('nombre estadístico o título de gráfica', self.metodo), ...}
        """
        pass

    @abc.abstractmethod
    def medidas_temporales(self):
        pass


class VariadorParametros(abc.ABC):
    """Clase variadora de parámetros, requiere parámetros fijos e iterables (metaparámetros a recorrer)"""

    @abc.abstractmethod
    def get_params(self, *args):
        """Obtener parámetros de la simulación, calculando los valores como fuera necesario"""
        pass

    @property
    def iterables_variacion(self):
        """Obtener la lista de los metaparámetros a iterar con el producto cartesiano"""
        valores = []
        for k in self.__dict__:
            o = self.__dict__[k]
            if hasattr(o, '__getitem__') or hasattr(o, '__iter__'):
                valores.append(o)
        return valores

    @staticmethod
    @abc.abstractmethod
    def obtener_clave(valores):
        """Convertir un conjunto de metaparámetros en una clave apta para identificar gráficas y demás"""
        pass

    @staticmethod
    @abc.abstractmethod
    def descr_parametros(clave):
        """Obtener texto descriptivo de los parámetros"""
        pass

    @staticmethod
    @abc.abstractmethod
    def descr_parametros_graf(clave):
        """Obtener texto descriptivo de los parámetros para gráficas"""
        pass

    def __iter__(self):
        for valores in itertools.product(*self.iterables_variacion):
            yield self.obtener_clave(valores), self.get_params(*valores)


class VariableEstadistica:
    """
    Variable estadística, puede contener:
    * Un valor numérico (un promedio)
    * Un conjunto de valores (una distribución de frecuencias):
        * Una lista de frecuencias (índice = valor)
        * Un diccionario de frecuencias (clave = valor)
    """

    def __init__(self, nombre, metodo, xlabel=None, ylabel=None, simbolo=None):
        self.nombre = nombre
        self.metodo = metodo
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.simbolo = simbolo
        self._datos = None

    @property
    def datos(self):
        if self._datos is None:
            self._instanciar()
        return self._datos

    def _instanciar(self):
        self._datos = self.metodo()

    def es_escalar(self):
        return np.isscalar(self.datos) or np.array(self.datos).ndim == 0

    def es_distribucion(self):
        return not self.es_escalar()

    def get_frecuencias(self):
        if self.es_escalar():
            return None
        if isinstance(self.datos, dict):
            return self.datos.keys(), self.datos.values()
        else:
            return range(len(self.datos)), self.datos


class VariableTemporal:
    def __init__(self, nombre, datos, xlabel=None, ylabel=None):
        self.nombre = nombre
        self.datos = datos
        self.xlabel = xlabel
        self.ylabel = ylabel


class Experimento:
    """Realizar un experimento con varias corridas de una simulación, variando los parámetros con un variador"""

    def __init__(self, clase, variador_parametros, corridas=10, **kwargs):
        self._clase = clase
        self.parametros = variador_parametros
        self.corridas = corridas
        self.simulaciones = {}
        # instanciar simulaciones, sin correrlas todavía
        for clave, (pargs, pkwargs) in self.parametros:
            # si hay, agregar parámetros fijos de diccionario adicionales
            for k in kwargs:
                pkwargs[k] = kwargs[k]
            self.simulaciones[clave] = [self._clase(*pargs, **pkwargs) for i in range(corridas)]

    def correr(self):
        """Correr las simulaciones del experimento"""
        print('Corriendo simulaciones...')
        for clave in tqdm(self.simulaciones):
            for sim in self.simulaciones[clave]:
                sim.correr()

    def reportar(self, en_vivo=True, nubes_temporales=True, confianza=0.95):
        for clave in self.simulaciones:
            print()
            print(f"Simulación: {self._clase.NOMBRE_MODELO} - {self.parametros.descr_parametros(clave)}, "
                  f"corridas: {self.corridas}")
            print()
            idx = np.random.randint(0, len(self.simulaciones[clave]) - 1)
            print(f'Resultados corrida n° {idx + 1} (seleccionada al azar):')
            self.simulaciones[clave][idx].informe()
            temporales = self.simulaciones[clave][idx].medidas_temporales()
            for k in temporales:
                var = temporales[k]
                titulo = var.nombre
                if en_vivo:
                    titulo += f' {self.parametros.descr_parametros_graf(clave)}'
                graf = GraficoDiscreto(titulo, xlabel=var.xlabel, ylabel=var.ylabel)
                graf.graficar(*var.datos)
                if not en_vivo:
                    nombre_archivo = f'{clave}_{k}_corrida_{idx + 1}'
                    graf.renderizar(nombre_archivo=nombre_archivo)
                    plt.close(graf.fig)
                if nubes_temporales:
                    titulo = f'{var.nombre} (nube de corridas)'
                    if en_vivo:
                        titulo += f' {self.parametros.descr_parametros_graf(clave)}'
                    graf_nube = GraficoDiscreto(titulo, xlabel=var.xlabel, ylabel=var.ylabel)
                    for sim in self.simulaciones[clave]:
                        var = sim.medidas_temporales()[k]
                        graf_nube.graficar(*var.datos)
                    if not en_vivo:
                        nombre_archivo = f'{self._clase.CLAVE}_{clave}_{k}_nube'
                        graf.renderizar(nombre_archivo=nombre_archivo)
                        plt.close(graf.fig)
            diccionario_medidas = self.simulaciones[clave][0].medidas_estadisticas()
            resultados = {}
            for k in diccionario_medidas:
                resultados[k] = []
            for sim in self.simulaciones[clave]:
                medidas_estadisticas = sim.medidas_estadisticas()
                for k in medidas_estadisticas:
                    var = medidas_estadisticas[k]
                    resultados[k].append(var.datos)
            print()
            print(f'Resultados experimento:')
            for k in resultados:
                if not hasattr(resultados[k][0], '__len__'):  # distribución de valores (promedios)
                    promedio_promedios = stathelper.mean(resultados[k])
                    print(f'{diccionario_medidas[k].nombre}: {promedio_promedios}, '
                          f'IC {int(confianza * 100)}%: {stathelper.intervalo_confianza(resultados[k], confianza)}')
                    xlabel = diccionario_medidas[k].xlabel
                    if xlabel is None:
                        xlabel = 'Valores'
                    titulo = diccionario_medidas[k].nombre
                    if en_vivo:
                        titulo += f', {self.parametros.descr_parametros_graf(clave)}'
                    graf = GraficoDistribucion(titulo, xlabel=xlabel)
                    graf.graficar(resultados[k], simbolo=diccionario_medidas[k].simbolo)
                    graf.legend()
                else:  # distribución de listas (distribuciones de frecuencia)
                    distribuciones_frec = resultados[k]
                    largo_max = max([len(d) for d in distribuciones_frec])
                    probs = [[] for _ in range(largo_max)]
                    for n in range(largo_max):
                        # cargamos las frecuencias obtenidas para cada valor
                        for d in distribuciones_frec:
                            probs[n].append(d[n] if n < len(d) else 0.0)
                    probs_err = [[], []]  # barras de error para las probabilidades
                    for n in range(largo_max):
                        # cambiamos las listas de frecuencia por su medias y obtenemos sus barras de error
                        p = stathelper.mean(probs[n])
                        ic = stathelper.intervalo_confianza(probs[n], confianza)
                        probs[n] = p
                        probs_err[0].append(p - ic[0])
                        probs_err[1].append(ic[1] - p)
                    xlabel = diccionario_medidas[k].xlabel
                    if xlabel is None:
                        xlabel = 'Valores'
                    titulo = diccionario_medidas[k].nombre
                    if en_vivo:
                        titulo += f', {self.parametros.descr_parametros_graf(clave)}'
                    graf = Plot(titulo, xlabel=xlabel, ylabel='Frecuencia relativa')
                    x = np.arange(0, len(probs))
                    graf.bar(x, probs, yerr=probs_err)
                    if len(x) <= 25:
                        graf.ax.set_xticks(x)
                    # noinspection PyUnresolvedReferences
                    intervalos = [(probs[i] - probs_err[0][i], probs[i] + probs_err[1][i]) for i in range(len(probs))]
                    print(f'{diccionario_medidas[k].nombre}: {probs}, IC {int(confianza * 100)}%: {intervalos}')
                if not en_vivo:
                    nombre_archivo = f'{self._clase.CLAVE}_{clave}_{k}'
                    graf.renderizar(nombre_archivo=nombre_archivo)
                    plt.close(graf.fig)
            if en_vivo:
                plt.show()
