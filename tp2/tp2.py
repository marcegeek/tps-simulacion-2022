import numpy as np
import matplotlib.pyplot as plt
import statistics as st


class Ruleta:
    def __init__(self):
        self.ultimoNumero=None

    def nuevoNumero(self):
        self.ultimoNumero=np.random.randint(0, 37)
        return self.ultimoNumero

    def esPar(self):
        return self.ultimoNumero%2==0

    def esImpar(self):
        return self.ultimoNumero%2==1

    def esNegro(self):
        return self.ultimoNumero in [2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35]

    def esRojo(self):
        return self.ultimoNumero!=0 and not self.esNegro()

def main():
    ruleta = Ruleta()
    print(ruleta.nuevoNumero())
    print(ruleta.esPar())


if __name__ == '__main__':
    main()
