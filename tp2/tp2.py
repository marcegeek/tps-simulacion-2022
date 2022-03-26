import numpy as np
import matplotlib.pyplot as plt
import statistics as st


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


class EstrategiaMartingala:
    APUESTA_INICIAL = 1

    def __init__(self, ruleta, jugador):
        self.ruleta = ruleta
        self.jugador = jugador
        self.cantidad = self.APUESTA_INICIAL

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


def main():
    ruleta = Ruleta()
    jugador = Jugador(ruleta, 10, color='rojo')
    estrategia = EstrategiaMartingala(ruleta, jugador)
    for i in range(10):
        ruleta.nuevoNumero()
        print(f'Jugador apostará {estrategia.cantidad}')
        estado = 'ganó' if estrategia.apostar() else 'perdió'
        print(f'Jugador {estado}, su capital actual es {jugador.capital}')
        if jugador.capital == 0:
            print('Jugador quebró')
            break


if __name__ == '__main__':
    main()
