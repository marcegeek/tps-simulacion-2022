import numpy as np
from simulacion import Evento, Simulacion


class EventoPartida(Evento):

    def __init__(self, tiempo, callback, servidor):
        super().__init__(tiempo, callback)
        self.servidor = servidor


class ColaMMC(Simulacion):
    ESTADO_DESOCUPADO, ESTADO_OCUPADO = 0, 1

    def __init__(self, servidores, tasa_arribos, tasa_servicio, semilla=None):
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

    def programar_arribo(self):
        self.eventos.append(
            Evento(self.reloj + self.np_randomstate.exponential(scale=1/self.tasa_arribos), self.arribo)
        )

    def programar_partida(self, servidor):
        self.eventos.append(
            EventoPartida(self.reloj + self.np_randomstate.exponential(scale=1/self.tasa_servicio), self.partida, servidor)
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

    def promedio_clientes_cola(self):
        return self.area_clientes_cola / self.reloj

    def utilizacion_servidor(self):
        return self.area_estados / self.reloj

    def correr(self, n_clientes):
        while self.clientes_completaron_demora < n_clientes:
            self.hacer_un_paso()

    def informe(self):
        print(f'Demora promedio en cola: {self.demora_promedio():17.3f} minutos')
        print(f'Número promedio de clientes en cola: {self.promedio_clientes_cola():.3f}')
        print(f'Utilización del servidor: {self.utilizacion_servidor():16.3f}')
        print(f'Tiempo de fin de la simulación: {self.reloj:12.3f}')


class ColaMM1(ColaMMC):

    def __init__(self, tasa_arribos, tasa_servicio, semilla=None):
        super().__init__(1, tasa_arribos, tasa_servicio, semilla=semilla)


def test():
    sim = ColaMM1(2, 4)
    sim.correr(1000)
    print('M/M/1:')
    sim.informe()
    print()

    sim = ColaMMC(2, 2, 4)
    sim.correr(1000)
    print('M/M/2:')
    sim.informe()


if __name__ == '__main__':
    test()
