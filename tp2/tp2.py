import numpy as np
import matplotlib.pyplot as plt
import statistics as st
import abc


class Ruleta:
    def __init__(self):
        self.ultimoNumero=None

    def nuevoNumero(self):
        self.ultimoNumero=np.random.randint(0, 37)
        return self.ultimoNumero

    def esNegro(self):
        return self.ultimoNumero in [2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35]

    def esRojo(self):
        return self.ultimoNumero!=0 and not self.esNegro()


class Jugador:

    def __init__(self, ruleta, capital_inicial, color='rojo'):
        self.ruleta = ruleta
        self.capital = capital_inicial
        self.color = color

    def apostar(self, cantidad):
        self.capital -= cantidad
        gane = self.ruleta.esRojo if self.color == 'rojo' else self.ruleta.esNegro
        if gane():
            self.capital += cantidad * 2
            return True
        else:
            return False


class Estrategia:
    APUESTA_INICIAL = 1
    nombre = 'Estrategia vacía'

    def __init__(self, ruleta, jugador):
        self.ruleta = ruleta
        self.jugador = jugador
        self.cantidad = self.APUESTA_INICIAL

    @abc.abstractmethod
    def apostar(self):
        pass


class EstrategiaMartingala (Estrategia):
    nombre = 'Martingala'

    def apostar(self):
        if not self.jugador.apostar(self.cantidad):
            if self.jugador.capital >= self.cantidad * 2:
                self.cantidad *= 2
            else:
                self.cantidad = self.jugador.capital
            return False
        else:
            self.cantidad = self.APUESTA_INICIAL
            return True



class EstrategiaDAlembert (Estrategia):
    nombre = 'D\'Alembert'

    def apostar(self):
        if not self.jugador.apostar(self.cantidad):
            if self.jugador.capital >= self.cantidad + 1:
                self.cantidad += 1
            else:
                self.cantidad = self.jugador.capital
            return False
        else:
            self.cantidad = self.APUESTA_INICIAL
            return True


class EstrategiaFibonacci(Estrategia):
    nombre = 'Fibonacci'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.generador = self._get_generador()
        self.secuencia = []
        # inicializar para primer apuesta
        self.index = 0
        self._avanzar(0)

    def apostar(self):
        if not self.jugador.apostar(self.cantidad):
            self._avanzar(1)
            if self.jugador.capital < self.cantidad:
                self.cantidad = self.jugador.capital
            return False
        else:
            self._retroceder(2)
            return True

    def _avanzar(self, n):
        self.index += n
        if self.index < 0:
            self.index = 0
        if self.index >= len(self.secuencia):
            for i in range(self.index - len(self.secuencia) + 1):
                self.secuencia.append(next(self.generador))
        self.cantidad = self.secuencia[self.index] * self.APUESTA_INICIAL

    def _retroceder(self, n):
        self._avanzar(-n)

    @staticmethod
    def _get_generador():
        a, b = 1, 1
        while True:
            yield a
            a, b = b, a + b


def probarEstrategia(estrategia,ruleta,rondas,capital):
    print('')
    print('Usando estrategia: '+estrategia.nombre)
    print('')
    jugador = Jugador(ruleta, capital, color='rojo' if np.random.random()>0.5 else 'negro')
    estrategia = estrategia(ruleta, jugador)
    for i in range(rondas):
        ruleta.nuevoNumero()
        print(f'Jugador apostará {estrategia.cantidad}')
        estado = 'ganó' if estrategia.apostar() else 'perdió'
        print(f'Jugador {estado}, su capital actual es {jugador.capital}')
        if jugador.capital == 0 and capital!=0:
            print('Jugador quebró')
            break

def main():
    ruleta = Ruleta()

    probarEstrategia(EstrategiaMartingala,ruleta,rondas=10,capital=10)

    probarEstrategia(EstrategiaDAlembert,ruleta,rondas=10,capital=10)

    probarEstrategia(EstrategiaFibonacci,ruleta,rondas=10,capital=10)

if __name__ == '__main__':
    main()
