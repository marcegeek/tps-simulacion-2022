import numpy as np
import matplotlib.pyplot as plt
import statistics as st

from simulacion import Evento, Simulacion, Experimento
from util.plotter import GraficoDistribucion, GraficoDiscreto


class EventoPartida(Evento):

    def __init__(self, tiempo, callback, servidor):
        super().__init__(tiempo, callback)
        self.servidor = servidor


class ColaMMC(Simulacion):
    ESTADO_DESOCUPADO, ESTADO_OCUPADO = 0, 1

    def __init__(self, servidores, tasa_arribos, tasa_servicio, num_clientes=1000, capacidad=None, semilla=None):
        super().__init__(semilla=semilla)
        self.tasa_arribos = tasa_arribos
        self.tasa_servicio = tasa_servicio
        self.capacidad = capacidad
        self.np_randomstate = np.random.RandomState(semilla)
        self.programar_arribo()  # evento arribo inicial

        self.tiempos_arribo = []
        self.estado_servidores = [self.ESTADO_DESOCUPADO] * servidores
        self.clientes_cola = 0
        self.clientes_cola_tiempo = [self.clientes_cola]
        self.clientes_denegados = 0
        self.clientes_denegados_tiempo = [self.clientes_denegados]
        self.tiempos_cola = [0.0]
        self.tiempos_denegados = [0.0]
        self.estados_servidores_tiempo = [[self.ESTADO_DESOCUPADO]] * servidores
        self.tiempos_servidores = [[0.0]] * servidores

        self.clientes_completaron_demora = 0
        self.demora_total = 0.
        self.area_clientes_cola = 0.
        self.area_estados = 0.
        self.total_tiempo_servicio = 0.

        self.num_clientes = num_clientes

    def programar_arribo(self):
        self.eventos.append(
            Evento(self.reloj + self.np_randomstate.exponential(scale=1/self.tasa_arribos), self.arribo)
        )

    def programar_partida(self, servidor):
        tiempo_servicio = self.np_randomstate.exponential(scale=1/self.tasa_servicio)
        self.total_tiempo_servicio += tiempo_servicio
        self.eventos.append(
            EventoPartida(self.reloj + tiempo_servicio, self.partida, servidor)
        )

    def arribo(self, ev):
        self.programar_arribo()
        if self.estado_servidores.count(self.ESTADO_OCUPADO) == len(self.estado_servidores):
            # todos los servidores ocupados, incrementar clientes en cola
            if self.capacidad is None or self.clientes_cola + 1 <= self.capacidad:  # comprobar capacidad de cola
                self.clientes_cola += 1
                self.tiempos_arribo.append(ev.tiempo)
                self.clientes_cola_tiempo.append(self.clientes_cola)
                self.tiempos_cola.append(self.reloj)
            else:
                self.clientes_denegados += 1
                self.clientes_denegados_tiempo.append(self.clientes_denegados)
                self.tiempos_denegados.append(self.reloj)
        else:
            # servidor desocupado, el cliente es atendido sin demora
            self.clientes_completaron_demora += 1
            self.servicio()

    def partida(self, ev):
        self.estado_servidores[ev.servidor] = self.ESTADO_DESOCUPADO
        self.estados_servidores_tiempo[ev.servidor].append(self.estado_servidores[ev.servidor])
        self.tiempos_servidores[ev.servidor].append(self.reloj)
        if self.clientes_cola != 0:
            # hay clientes en cola, el primero pasa a ser atendido
            self.clientes_cola -= 1
            self.demora_total += ev.tiempo - self.tiempos_arribo.pop(0)
            self.clientes_completaron_demora += 1
            self.clientes_cola_tiempo.append(self.clientes_cola)
            self.tiempos_cola.append(self.reloj)
            self.servicio()

    def determinar_servidor(self):
        # de los servidores desocupados, seleccionar al azar con distribución uniforme
        serv_desocupados = [i for i in range(len(self.estado_servidores)) if self.estado_servidores[i] == self.ESTADO_DESOCUPADO]
        return self.np_randomstate.choice(serv_desocupados)

    def servicio(self):
        servidor = self.determinar_servidor()
        self.estado_servidores[servidor] = self.ESTADO_OCUPADO
        self.programar_partida(servidor)
        self.estados_servidores_tiempo[servidor].append(self.estado_servidores[servidor])
        self.tiempos_servidores[servidor].append(self.reloj)

    def actualizar_estadisticas(self):
        super().actualizar_estadisticas()
        self.area_clientes_cola += self.clientes_cola * self.tiempo_desde_ult_evento
        self.area_estados += sum(self.estado_servidores)/len(self.estado_servidores) * self.tiempo_desde_ult_evento

    def demora_promedio(self):
        return self.demora_total / self.clientes_completaron_demora

    def tiempo_promedio_servicio(self):
        return self.total_tiempo_servicio / self.clientes_completaron_demora

    def tiempo_promedio_sistema(self):
        return self.demora_promedio() + self.tiempo_promedio_servicio()

    def promedio_clientes_cola(self):
        return self.area_clientes_cola / self.reloj

    def promedio_clientes_sistema(self):
        return self.promedio_clientes_cola() + self.utilizacion_servidor() * len(self.estado_servidores)

    def utilizacion_servidor(self):
        return self.area_estados / self.reloj

    def tasa_global_arribos(self):
        beta, _ = np.polyfit(self.tiempos_cola, self.clientes_cola_tiempo, 1)
        return beta

    def denegacion_servicio(self):
        return self.clientes_denegados / self.clientes_completaron_demora

    def es_fin(self):
        return self.clientes_completaron_demora >= self.num_clientes

    def informe(self):
        capacidad = '∞' if self.capacidad is None else self.capacidad
        print(f'Modelo de colas M/M/{len(self.estado_servidores)}/{capacidad}')
        print(f'Tasa de arribos: {self.tasa_arribos:31.3f} clientes/min')
        print(f'Tasa de servicio: {self.tasa_servicio:30.3f} clientes/min')
        print(f'Número de clientes: {self.num_clientes:27}')
        print('\nResultados de la simulación:')
        print(f'Tiempo promedio en cola: {self.demora_promedio():23.3f} minutos')
        print(f'Tiempo promedio en el sistema: {self.tiempo_promedio_sistema():17.3f}')
        print(f'Número promedio de clientes en cola: {self.promedio_clientes_cola():11.3f}')
        print(f'Número promedio de clientes en el sistema: {self.promedio_clientes_sistema():5.3f}')
        print(f'Tasa global de arribos: {self.tasa_global_arribos()}')
        if self.capacidad is not None:
            print(f'Probabilidad de denegación de servicio: {self.denegacion_servicio():8.3f}')
        print('Utilización de', end='')
        if len(self.estado_servidores) == 1:
            print('l servidor: ', end='')
            padding = 22
        else:
            print(' los servidores: ', end='')
            padding = 17
        print(f'{self.utilizacion_servidor():{padding}.3f}')
        print(f'Tiempo de fin de la simulación: {self.reloj:18.3f}')


class ColaMM1(ColaMMC):

    def __init__(self, tasa_arribos, tasa_servicio, num_clientes=1000, capacidad=None, semilla=None):
        super().__init__(1, tasa_arribos, tasa_servicio, num_clientes=num_clientes, capacidad=capacidad, semilla=semilla)


def realizar_experimento(tasa_servicio, factor, num_clientes, capacidad=None, corridas=100):
    tasa_arribos = tasa_servicio * factor
    exp = Experimento(ColaMM1, [tasa_arribos, tasa_servicio], {'num_clientes': num_clientes, 'capacidad': capacidad},
                      corridas=corridas)
    exp.correr()
    print(f'Cola M/M/1/{"∞" if capacidad is None else capacidad}')
    print(f'Tasa de arribos/tasa de servicio: {factor * 100}%')
    idx = np.random.randint(0, len(exp.resultados) - 1)
    print(f'Resultados corrida n° {idx + 1}:')
    exp.resultados[idx].informe()

    promedios_clientes_cola = []
    promedios_espera_cola = []
    promedios_tiempo_sistema = []
    promedios_tiempo_servicio = []
    tasas_globales_arribos = []

    graf_clientes = GraficoDiscreto('Clientes en cola a lo largo del tiempo', xlabel='Tiempo [minutos]', ylabel='Clientes')
    for cola in exp.resultados:
        prom_clientes_cola = cola.promedio_clientes_cola()
        prom_espera = cola.demora_promedio()
        prom_sistema = cola.tiempo_promedio_sistema()
        prom_tiempo_servicio = cola.tiempo_promedio_servicio()
        graf_clientes.graficar(cola.tiempos_cola, cola.clientes_cola_tiempo)
        promedios_clientes_cola.append(prom_clientes_cola)
        promedios_espera_cola.append(prom_espera)
        promedios_tiempo_sistema.append(prom_sistema)
        promedios_tiempo_servicio.append(prom_tiempo_servicio)
        tasas_globales_arribos.append(cola.tasa_global_arribos())
    graf_clientes.legend()
    graf_clientes.renderizar(nombre_archivo='clientes')
    diccionario_graficas = {
        'promedio-clientes-cola': ('Promedio de clientes en cola', promedios_clientes_cola),
        'tiempo-promedio-cola': ('Tiempo promedio en cola', promedios_espera_cola),
        'tiempo-promedio-sistema': ('Tiempo promedio en el sistema', promedios_tiempo_sistema),
        'tiempo-promedio-servicio': ('Tiempo promedio de servicio', promedios_tiempo_servicio),
        'tasa-global-arribos-promedio': ('Tasa global de arribos promedio', tasas_globales_arribos),
    }
    for archivo in diccionario_graficas:
        nombre, prom = diccionario_graficas[archivo]
        graf = GraficoDistribucion(nombre, xlabel='Promedios muestrales')
        graf.graficar(prom)
        graf.legend()
        graf.renderizar(nombre_archivo=archivo)
    """mean_mean = st.mean(promedios_clientes_cola)
    mean_std = st.stdev(promedios_clientes_cola)
    print(f'Promedio los promedios: {mean_mean}')
    print(f'Desvío estándar: {mean_std}')
    print(f'Tasa promedio general: {st.mean(tasas_globales_arribos)}')
    print(f'Desvío estándar: {st.stdev(tasas_globales_arribos)}')
    print(
        f'IC_95% clientes en cola {mean_mean} +- {1.96 * mean_std}: {mean_mean - 1.96 * mean_std}, {mean_mean + 1.96 * mean_std}')"""
    #plt.show()


def main(num_clientes=1000, corridas=100):
    tasa_servicio = 1 / 3  # "1/3" cliente por minuto -> 3 min por cliente
    # for factor in [0.25, 0.5, 0.75, 1, 1.25]:
    #for factor in [1.25]:
    for factor in [0.25]:
        realizar_experimento(tasa_servicio, factor, num_clientes, corridas=corridas)


def _test():
    # print('M/M/1:')
    sim = ColaMM1(2, 4)
    sim.correr()
    print()

    # print('M/M/2:')
    sim = ColaMMC(2, 2, 4)
    sim.correr()


if __name__ == '__main__':
    main()
