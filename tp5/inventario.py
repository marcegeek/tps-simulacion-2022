from simulacion import Evento, Simulacion, Experimento, VariadorParametros, VariableEstadistica, VariableTemporal


class EventoArriboPedido(Evento):
    def __init__(self, tiempo, callback, cantidad):
        super().__init__(tiempo, callback)
        self.cantidad = cantidad


class ModeloInventario(Simulacion):
    NOMBRE_MODELO = "Inventario producto único"

    def __init__(self, meses=120, nivel_inventario=60, bigs=40, smalls=20, setup_cost=32, costo_incremental=3,
                 costo_mantenimiento=1, costo_reserva=5, rango_lag=(0.5, 1),
                 media_entredemanda=0.1, distribucion_demanda=((1, 2, 3, 4), (1/6, 1/3, 1/3, 1/6)), semilla=None):
        super().__init__(semilla=semilla)
        self.nivel_inventario = nivel_inventario
        self.niveles_inventario = [nivel_inventario]
        self.tiempos = [0.0]
        self.meses = meses
        self.bigs = bigs
        self.smalls = smalls
        self.setup_cost = setup_cost
        self.costo_incremental = costo_incremental
        self.costo_mantenimiento = costo_mantenimiento
        self.costo_reserva = costo_reserva
        self.rango_lag = rango_lag
        self.media_entredemanda = media_entredemanda
        self.distribucion_demanda = distribucion_demanda

        self.costo_total_ordenado = 0
        self.mantenidos_area = 0
        self.area_escasez = 0

        self.eventos.append(Evento(0.0, self.evaluar))  # evaluación inicial (inicio primer mes)
        self.programar_demanda()  # demanda inicial

    def programar_evaluacion(self):
        tiempo = self.reloj + 1
        if tiempo < self.meses:  # al final de la simulación no se evalúa más
            self.eventos.append(Evento(tiempo, self.evaluar))

    def programar_arribo_pedido(self, cantidad):
        self.eventos.append(
            EventoArriboPedido(
                self.reloj + self.np_randomstate.uniform(self.rango_lag[0], self.rango_lag[1]),
                self.arribo_pedido,
                cantidad)
        )

    def arribo_pedido(self, ev: EventoArriboPedido):
        self.nivel_inventario += ev.cantidad
        self.tiempos.append(self.reloj)
        self.niveles_inventario.append(self.nivel_inventario)

    def demanda(self, ev):
        self.programar_demanda()
        valores, distribucion = self.distribucion_demanda
        distribucion_acumulada = [0] + [sum(distribucion[:i]) for i in range(1, len(distribucion) + 1)]
        r = self.np_randomstate.random()
        for i in range(len(distribucion_acumulada) - 1):
            if distribucion_acumulada[i] <= r < distribucion_acumulada[i + 1]:
                break
        # noinspection PyUnboundLocalVariable
        cant_demand = valores[i]
        self.nivel_inventario -= cant_demand
        self.tiempos.append(self.reloj)
        self.niveles_inventario.append(self.nivel_inventario)

    def programar_demanda(self):
        self.eventos.append(
            Evento(self.reloj + self.np_randomstate.exponential(scale=self.media_entredemanda), self.demanda)
        )

    def evaluar(self, ev):
        if self.nivel_inventario < self.smalls:
            cantidad = self.bigs - self.nivel_inventario
            self.costo_total_ordenado += self.setup_cost + self.costo_incremental * cantidad
            self.programar_arribo_pedido(cantidad)
        self.programar_evaluacion()

    def costo_ordenes_prom(self):
        return self.costo_total_ordenado / self.meses

    def costo_mantenimiento_prom(self):
        return self.costo_mantenimiento * self.mantenidos_area / self.meses

    def costo_escasez_prom(self):
        return self.costo_reserva * self.area_escasez / self.meses

    def costo_total(self):
        return self.costo_ordenes_prom() + self.costo_mantenimiento_prom() + self.costo_escasez_prom()

    def medidas_estadisticas(self):
        return {
            "costo_ordenes_prom": VariableEstadistica("Costo de orden promedio", self.costo_ordenes_prom),
            "costo_escasez_prom": VariableEstadistica("Costo escasez promedio", self.costo_escasez_prom),
            "costo_total": VariableEstadistica("Costo total", self.costo_total),
        }

    def medidas_temporales(self):
        # TODO completar
        return {}

    def informe(self):
        costo_ordenes_prom = self.costo_total_ordenado / self.meses
        costo_mantenimiento_prom = self.costo_mantenimiento * self.mantenidos_area / self.meses
        costo_escasez_prom = self.costo_reserva * self.area_escasez / self.meses
        costo_total = costo_ordenes_prom + costo_mantenimiento_prom + costo_escasez_prom
        print('Modelo de inventario de producto único')
        print(f'Nivel de inicial inventario: {self.niveles_inventario[0]}')
        print(f'Tiempo medio entre demandas: {self.media_entredemanda}')
        print(f'Distribución de la demanda: {self.distribucion_demanda}')
        print(f'Política de pedido: {(self.smalls, self.bigs)}')
        print(f'Costo de establecimiento de pedido: {self.setup_cost}')
        print(f'Costo incremental: {self.costo_incremental}')
        print(f'Costo de mantenimiento: {self.costo_mantenimiento}')
        print(f'Costo de faltante: {self.costo_reserva}')
        print(f'Rango distribución de demora de pedido: {list(self.rango_lag)}')
        print(f'Cantidad total de períodos: {self.meses}')
        print('\nResultados de la simulación:')
        print(f'Costo orden promedio: {costo_ordenes_prom}')
        print(f'Costo mantenimiento promedio: {costo_mantenimiento_prom}')
        print(f'Costo escasez promedio: {costo_escasez_prom}')
        print(f'Costo total: {costo_total}')

    def actualizar_estadisticas(self):
        super().actualizar_estadisticas()
        if self.nivel_inventario < 0:
            self.area_escasez -= self.nivel_inventario * self.tiempo_desde_ult_evento
        elif self.nivel_inventario > 0:
            self.mantenidos_area += self.nivel_inventario * self.tiempo_desde_ult_evento

    def es_fin(self):
        return self.reloj >= self.meses


def _test():
    inventario = ModeloInventario()
    inventario.correr()


class VariadorInventario(VariadorParametros):
    def __init__(self, smalls_arr, bigs_minus_smalls_arr):
        self.smalls_arr = smalls_arr
        self.bigs_minus_smalls_arr = bigs_minus_smalls_arr

    def get_params(self, smalls, bigs_minus_smalls):
        return (), {'smalls': smalls, 'bigs': smalls + bigs_minus_smalls}

    @staticmethod
    def obtener_clave(valores):
        smalls, bigs_minus_smalls = valores
        bigs = bigs_minus_smalls + smalls
        return f'{smalls}_{bigs}'

    @classmethod
    def descr_parametros(cls, clave):
        smalls, bigs = clave.split('_')
        return f'(s, S = {smalls}, {bigs})'

    @classmethod
    def descr_parametros_graf(cls, clave):
        return f'${cls.descr_parametros(clave)}$'


def main():
    smalls_arr = [20, 40, 60]
    bigs_minus_smalls_arr = [20, 40, 60, 80]
    variador = VariadorInventario(smalls_arr, bigs_minus_smalls_arr)
    exp = Experimento(ModeloInventario, variador, corridas=100)
    exp.correr()
    exp.reportar(en_vivo=False)


if __name__ == '__main__':
    main()
