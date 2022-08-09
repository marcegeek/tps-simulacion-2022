import numpy as np

from simulacion import Evento, Simulacion, Experimento, VariadorParametros, VariableEstadistica, VariableTemporal


class EventoPartida(Evento):

    def __init__(self, tiempo, callback, servidor):
        super().__init__(tiempo, callback)
        self.servidor = servidor


class ColaMMC(Simulacion):
    NOMBRE_MODELO = 'M/M/c'
    CLAVE = 'mmc'
    ESTADO_DESOCUPADO, ESTADO_OCUPADO = 0, 1

    def __init__(self, servidores, tasa_arribos, tasa_servicio, num_clientes=1000, capacidad=np.inf, semilla=None):
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
        self.estados_servidores_tiempo = [[self.ESTADO_DESOCUPADO]] * servidores

        self.clientes_completaron_demora = 0
        self.demora_total = 0.
        self.area_clientes_cola = 0.
        self.area_estados = 0.
        self.total_tiempo_servicio = 0.

        self.num_clientes = num_clientes

    def programar_arribo(self):
        self.eventos.append(
            Evento(self.reloj + self.np_randomstate.exponential(scale=1 / self.tasa_arribos), self.arribo)
        )

    def programar_partida(self, servidor):
        tiempo_servicio = self.np_randomstate.exponential(scale=1 / self.tasa_servicio)
        self.total_tiempo_servicio += tiempo_servicio
        self.eventos.append(
            EventoPartida(self.reloj + tiempo_servicio, self.partida, servidor)
        )

    def arribo(self, ev):
        self.programar_arribo()
        if self.estado_servidores.count(self.ESTADO_OCUPADO) == len(self.estado_servidores):
            # todos los servidores ocupados, incrementar clientes en cola
            if self.capacidad == np.inf or self.clientes_cola + 1 <= self.capacidad:  # comprobar capacidad de cola
                self.clientes_cola += 1
                self.tiempos_arribo.append(ev.tiempo)
            else:
                self.clientes_denegados += 1
        else:
            # servidor desocupado, el cliente es atendido sin demora
            self.clientes_completaron_demora += 1
            self.servicio()

    def partida(self, ev):
        self.estado_servidores[ev.servidor] = self.ESTADO_DESOCUPADO
        if self.clientes_cola != 0:
            # hay clientes en cola, el primero pasa a ser atendido
            self.clientes_cola -= 1
            self.demora_total += ev.tiempo - self.tiempos_arribo.pop(0)
            self.clientes_completaron_demora += 1
            self.servicio()

    def determinar_servidor(self):
        # de los servidores desocupados, seleccionar al azar con distribución uniforme
        serv_desocupados = [i for i in range(len(self.estado_servidores)) if
                            self.estado_servidores[i] == self.ESTADO_DESOCUPADO]
        return self.np_randomstate.choice(serv_desocupados)

    def servicio(self):
        servidor = self.determinar_servidor()
        self.estado_servidores[servidor] = self.ESTADO_OCUPADO
        self.programar_partida(servidor)

    def actualizar_estadisticas(self):
        super().actualizar_estadisticas()
        self.clientes_cola_tiempo.append(self.clientes_cola)
        self.clientes_denegados_tiempo.append(self.clientes_denegados)
        for i in range(len(self.estado_servidores)):
            self.estados_servidores_tiempo[i].append(self.estado_servidores[i])
        self.area_clientes_cola += self.clientes_cola * self.tiempo_desde_ult_evento
        self.area_estados += sum(self.estado_servidores) / len(self.estado_servidores) * self.tiempo_desde_ult_evento

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
        beta = 0.0
        if len(self.tiempos) > 1:
            beta = np.polyfit(self.tiempos, self.clientes_cola_tiempo, 1)[0]
        return beta

    def denegacion_servicio(self):
        return self.clientes_denegados / self.clientes_completaron_demora

    def probabilidades_clientes(self):
        """
        Devolver una lista con la distribución de frecuencias de la cantidad de clientes en cola.
        Los índices representan las cantidades respectivas.
        """
        tiempo_total = 0
        tiempos_totales_n = [0] * (max(self.clientes_cola_tiempo) + 1)
        probs = []
        for i in range(1, len(self.tiempos)):
            tiempo_i = self.tiempos[i] - self.tiempos[i - 1]
            for n in range(len(tiempos_totales_n)):
                if self.clientes_cola_tiempo[i] == n:
                    tiempos_totales_n[n] += tiempo_i
            tiempo_total += tiempo_i
        for t in tiempos_totales_n:
            probs.append(t/tiempo_total)
        return probs

    def probabilidad_n_clientes(self, n):
        probs = self.probabilidades_clientes()
        return probs[n] if n < len(probs) else 0.0

    def es_fin(self):
        return self.clientes_completaron_demora >= self.num_clientes

    def medidas_estadisticas(self):
        medidas = {
            "demora_promedio": VariableEstadistica("Demora promedio esperada en cola", self.demora_promedio, simbolo=r'$\hat{d}(n)$', xlabel='Tiempo [minutos]'),
            "tiempo_promedio_sistema": VariableEstadistica("Tiempo promedio en el sistema", self.tiempo_promedio_sistema, simbolo=r'$\hat{d}(n) + \hat{s}(n)$', xlabel='Tiempo [minutos]'),
            'n_promedio_clientes_cola': VariableEstadistica('Cantidad de clientes en cola en promedio', self.promedio_clientes_cola, simbolo=r'$\hat{q}(n)$', xlabel='Cantidad de clientes'),
            'tiempo_promedio_servicio': VariableEstadistica('Tiempo promedio de servicio', self.tiempo_promedio_servicio, simbolo=r'$\hat{s}(n)$', xlabel='Tiempo [minutos]'),
            'n_promedio_clientes_sistema': VariableEstadistica('Promedio de clientes en el sistema', self.promedio_clientes_sistema, simbolo=r'$\hat{q}(n) + \hat{u}(n)$', xlabel='Cantidad de clientes'),
            'utilizacion_servidor': VariableEstadistica('Ocupación del servidor', self.utilizacion_servidor, simbolo=r'$\hat{u}(n)$'),
            'probabilidad_n_clientes': VariableEstadistica('Probabilidad de encontrar n clientes en cola', self.probabilidades_clientes, xlabel='n', simbolo=r'$\hat{p}(Q(t) = n$'),
            'probabilidad_denegacion': VariableEstadistica('Probabilidad de denegación del servicio', self.denegacion_servicio, simbolo=r'$\hat{p}(den)$'),
            'tasa_global_arribos_promedio': VariableEstadistica('Tasa global de arribos promedio', self.tasa_global_arribos, simbolo=r'${\hat{T}_a}_g(n)$'),
        }
        if self.capacidad == np.inf:
            medidas.pop('probabilidad_denegacion')
        elif self.capacidad == 0:
            medidas.pop('demora_promedio')
            medidas.pop('n_promedio_clientes_cola')
            medidas.pop('probabilidad_n_clientes')
            medidas.pop('tasa_global_arribos_promedio')
        return medidas

    def medidas_temporales(self):
        medidas = {
            "n_clientes_cola_tiempo": VariableTemporal('Cantidad de clientes en cola a lo largo del tiempo', (self.tiempos, self.clientes_cola_tiempo), xlabel='Tiempo [minutos]', ylabel='Cantidad de clientes'),
            "n_denegados_tiempo": VariableTemporal('Cantidad acumulada de clientes denegados a lo largo del tiempo', (self.tiempos, self.clientes_denegados_tiempo), xlabel='Tiempo [minutos]', ylabel='Cantidad de clientes'),
        }
        if self.capacidad == np.inf:
            medidas.pop('n_denegados_tiempo')
        elif self.capacidad == 0:
            medidas.pop('n_clientes_cola_tiempo')
        return medidas

    def informe(self):
        capacidad = '∞' if self.capacidad == np.inf else self.capacidad
        print(f'Modelo de colas M/M/{len(self.estado_servidores)}/{capacidad}')
        print(f'Tasa de arribos: {self.tasa_arribos:31.3f} clientes/min')
        print(f'Tasa de servicio: {self.tasa_servicio:30.3f} clientes/min')
        print(f'Número de clientes: {self.num_clientes:27}')
        print('\nResultados de la simulación:')
        print(f'Tiempo promedio en cola: {self.demora_promedio():23.3f} minutos')
        print(f'Tiempo promedio en el sistema: {self.tiempo_promedio_sistema():17.3f}')
        print(f'Número promedio de clientes en cola: {self.promedio_clientes_cola():11.3f}')
        print(f'Número promedio de clientes en el sistema: {self.promedio_clientes_sistema():5.3f}')
        #print(f'Tasa global de arribos: {self.tasa_global_arribos()}')
        if self.capacidad != np.inf:
            print(f'Probabilidad de denegación de servicio: {self.denegacion_servicio():8.3f}')
        print('Utilización de', end='')
        if len(self.estado_servidores) == 1:
            print('l servidor: ', end='')
            padding = 22
        else:
            print(' los servidores: ', end='')
            padding = 17
        print(f'{self.utilizacion_servidor():{padding}.3f}')
        for i in range(max(self.clientes_cola_tiempo) + 1):
            print(f'Probabilidad {i} clientes en cola: {self.probabilidad_n_clientes(i)}')
        print(f'Tiempo de fin de la simulación: {self.reloj:18.3f}')


class ColaMM1(ColaMMC):
    NOMBRE_MODELO = 'M/M/1'
    CLAVE = 'mm1'

    def __init__(self, tasa_arribos, tasa_servicio, num_clientes=1000, capacidad=np.inf, semilla=None):
        super().__init__(1, tasa_arribos, tasa_servicio, num_clientes=num_clientes, capacidad=capacidad,
                         semilla=semilla)


class VariadorMM1(VariadorParametros):
    def __init__(self, tasa_servicio, taoverts_arr, capacidades):
        self.tasa_servicio = tasa_servicio
        self.taoverts_arr = taoverts_arr
        self.capacidades = capacidades

    def get_params(self, taoverts, capacidad):
        return (self.tasa_servicio * taoverts, self.tasa_servicio), {'capacidad': capacidad}

    @staticmethod
    def obtener_clave(valores):
        ta_over_ts, capacidad = valores
        return f'{int(ta_over_ts * 100)}_{capacidad}'

    @staticmethod
    def descr_parametros(clave):
        ta_over_ts, capacidad = clave.split('_')
        return f'Ta/Ts = {ta_over_ts}%, cap = {capacidad}'

    @staticmethod
    def descr_parametros_graf(clave):
        ta_over_ts, capacidad = clave.split('_')
        if capacidad == str(np.inf):
            capacidad = '\\infty'
        return f'$\\frac{{T_{{a}}}}{{T_{{s}}}} = {ta_over_ts}\\%$, $cap={capacidad}$'


def realizar_experimento(tasa_servicio, ta_over_ts_arr, capacidades, num_clientes=1000, corridas=100, en_vivo=False):
    exp = Experimento(ColaMM1, VariadorMM1(tasa_servicio, ta_over_ts_arr, capacidades), num_clientes=num_clientes, corridas=corridas)
    exp.correr()
    exp.reportar(en_vivo=en_vivo)


def main():
    # Duración del servicio: ~ Exp(0.5') -> tasa: 1/0.5' = 2 clientes/min
    tasa_servicio = 2
    num_clientes = 1000
    corridas = 100
    ta_over_ts_arr = [0.25, 0.5, 0.75, 1, 1.25]
    capacidades = [np.inf, 0, 2, 5, 10, 50]
    en_vivo = False
    realizar_experimento(tasa_servicio, ta_over_ts_arr, capacidades, num_clientes=num_clientes, corridas=corridas, en_vivo=en_vivo)


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
