import numpy as np
from simulacion import Evento, Simulacion


class EventoPartida(Evento):

    def __init__(self, tiempo, callback, servidor):
        super().__init__(tiempo, callback)
        self.servidor = servidor


class ColaMMC(Simulacion):
    ESTADO_DESOCUPADO, ESTADO_OCUPADO = 0, 1

    def __init__(self, servidores, tasa_arribos, tasa_servicio, num_clientes=1000, semilla=None):
        super().__init__()
        self.tasa_arribos = tasa_arribos
        self.tasa_servicio = tasa_servicio
        self.np_randomstate = np.random.RandomState(semilla)
        self.programar_arribo()  # evento arribo inicial

        self.tiempos_arribo = []
        self.estado_servidores = [self.ESTADO_DESOCUPADO] * servidores
        self.clientes_cola = 0

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
            self.clientes_cola += 1
            self.tiempos_arribo.append(ev.tiempo)
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
        serv_desocupados = [i for i in range(len(self.estado_servidores)) if self.estado_servidores[i] == self.ESTADO_DESOCUPADO]
        return self.np_randomstate.choice(serv_desocupados)

    def servicio(self):
        servidor = self.determinar_servidor()
        self.estado_servidores[servidor] = self.ESTADO_OCUPADO
        self.programar_partida(servidor)

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

    def correr(self):
        while self.clientes_completaron_demora < self.num_clientes:
            self.hacer_un_paso()
        self.informe()

    def informe(self):
        print(f'Modelo de colas M/M/{len(self.estado_servidores)}')
        print(f'Tasa de arribos: {self.tasa_arribos:31.3f} clientes/min')
        print(f'Tasa de servicio: {self.tasa_servicio:30.3f} clientes/min')
        print(f'Número de clientes: {self.num_clientes:27}')
        print('\nResultados de la simulación:')
        print(f'Tiempo promedio en cola: {self.demora_promedio():23.3f} minutos')
        print(f'Tiempo promedio en el sistema: {self.tiempo_promedio_sistema():17.3f}')
        print(f'Número promedio de clientes en cola: {self.promedio_clientes_cola():11.3f}')
        print(f'Número promedio de clientes en el sistema: {self.promedio_clientes_sistema():5.3f}')
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

    def __init__(self, tasa_arribos, tasa_servicio, num_clientes=1000, semilla=None):
        super().__init__(1, tasa_arribos, tasa_servicio, num_clientes=num_clientes, semilla=semilla)


def test():
    # print('M/M/1:')
    sim = ColaMM1(2, 4)
    sim.correr()
    print()

    # print('M/M/2:')
    sim = ColaMMC(2, 2, 4)
    sim.correr()


if __name__ == '__main__':
    test()
