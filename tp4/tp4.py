from random import random
import math
import scipy.stats
from scipy.stats import norm
import matplotlib.pyplot as plt


def uniforme(a, b, rep: int = 1):
    x = []
    for i in range(rep):
        x.append(a + (b - a) * (round(random(), 4)))
    return x


def exponencial(ex, rep: int = 1):
    x = []
    for i in range(rep):
        x.append(-ex * math.log(round(random(), 4)))
    return x


def gamma(k, a, rep: int = 1):
    x = []
    for i in range(1, rep):
        tr = 1
        for j in range(1, k):
            tr *= random()
        x.append(-(math.log(tr)) / a)
    return x


def normal(ex, stdx, rep: int = 1):
    x = []
    for i in range(rep):
        sm = 0
        for j in range(12):
            sm += random()
        x.append(stdx * (sm - 6) + ex)
    return x


def pascal(k, q, rep: int = 1):
    nx = []
    for i in range(rep):
        tr = 1
        for j in range(k):
            tr *= random()
        x = math.log(tr) // math.log(q)
        nx.append(x)
    return nx


def binomial(n, p, rep: int = 1):
    x = []
    for i in range(rep):
        y = 0
        for j in range(1, n):
            if (random() - p) < 0:
                y += 1
        x.append(y)
    return x


def hipergeometrica(tn, ns, p, rep: int = 1):
    x = []
    for i in range(rep):
        tn1 = tn
        ns1 = ns
        p1 = p
        y = 0
        for j in range(1, ns1):
            if (random() - p1) > 0:
                s = 0
            else:
                s = 1
                y += 1
            p1 = (tn1 * p1 - s) / (tn1 - 1)
            tn1 -= 1
        x.append(y)
    return x


def poisson(lamb, rep: int = 1):
    x = []
    for i in range(rep):
        cont = 0
        tr = 1
        b = 0
        while tr - b >= 0:
            b = math.exp(-lamb)
            tr *= random()
            if tr - b >= 0:
                cont += 1
        x.append(cont)
    return x


def empirica_discreta(rep: int = 1):
    x = []
    p = [0.273, 0.037, 0.195, 0.009, 0.124, 0.058, 0.062, 0.151, 0.047, 0.044]
    for i in range(rep):
        a = 0
        z = 1
        for j in p:
            a += j
            if random() <= a:
                break
            else:
                z += 1
        x.append(z)
    return x


def TestChiCuadUni(u):
    """Test de bondad Chi Cuadrado para distribucion uniforme"""
    observado = []
    esperado = 100
    c = 1.2
    chiquadesperado = round(scipy.stats.chi2.ppf(1 - 0.05, 9), 2)
    for i in range(10):
        x = 0
        for j in range(len(u)):
            if (c - 0.2) <= float(u[j]) <= c:
                x += 1
        observado.append(x)
        c += 0.2
    x2 = 0
    print("Valor chi cuadrados:")
    for i in range(len(observado)):
        x1 = (((observado[i] - esperado) ** 2) / esperado)
        x2 += x1
        print(x2)

    print("Uniforme")
    print("Observado")
    print(observado)
    print("Esperado")
    print(esperado)
    print("Valor de X2 obtenido = " + str(x2))
    print("Se poseen 10 intervalos, por lo tantos tendremos 9 grados de libertad.")
    print("Con 9 grados de libertad y con un 95 porciento de confianza se obtiene un valor de Chi cuadrado de 16.92")
    if x2 < chiquadesperado:
        print("El valor de chi cuadrado obtenido: " + str(x2) +
              " es menor que " + str(chiquadesperado) + " ,por lo tanto Paso el test")
    else:
        print("No paso el test")


def TestChiCuadExp(u):
    """Test de bondad Chi Cuadrado para distribucion exponencial"""
    observado = []
    esperado = []
    c = 0.3
    chiquadesperado = round(scipy.stats.chi2.ppf(1 - 0.05, 9), 2)
    for i in range(9):
        x = 0
        for j in range(len(u)):
            if (c - 0.3) <= float(u[j]) <= c:
                x += 1
        observado.append(x)
        esperado.append(1000 * ((1 - math.e ** (-(1 / 5) * c)) - (1 - math.e ** (-(1 / 5) * (c - 0.3)))))
        c += 0.3
    observado.append(1000 - sum(observado))
    esperado.append(1000 * (math.e ** (-(1 / 5) * (c - 0.3))))
    x2 = 0
    print("Valor chi cuadrados:")
    for i in range(len(observado)):
        x1 = (((observado[i] - esperado[i]) ** 2) / esperado[i])
        x2 += x1
        print(x2)

    print("Exponencial")
    print("Observado")
    print(observado)
    print("Esperado")
    print(esperado)
    print("Valor de X2 obtenido = " + str(x2))
    print("Se poseen 10 intervalos, por lo tantos tendremos 9 grados de libertad.")
    print("Con 9 grados de libertad y con un 95 porciento de confianza se obtiene un valor de Chi cuadrado de 16.92")
    if x2 < chiquadesperado:
        print("El valor de chi cuadrado obtenido: " + str(x2) +
              " es menor que " + str(chiquadesperado) + " ,por lo tanto Paso el test")
    else:
        print("No paso el test")


def TestChiCuadNormal(u):
    """Test de bondad Chi Cuadrado para distribucion Normal"""
    observado = []
    esperado = []
    a1 = 0
    a2 = 0
    chiquadesperado = round(scipy.stats.chi2.ppf(1 - 0.05, 9), 2)
    c = -80
    for i in range(10):
        x = 0
        for j in range(len(u)):
            if (c - 20) <= float(u[j]) <= c:
                x += 1
        observado.append(x)
        a1 += (c - 10) * x
        a2 += ((c - 10) ** 2) * x
        c += 20
    a1 = a1 / 1000
    a2 = a2 / 1000
    desviacion = math.sqrt(a2 - a1 ** 2)
    media = a1
    c = -80
    esperado = []
    for i in range(10):
        esperado.append(1000 * (norm.cdf((c - media) / desviacion) - norm.cdf(((c - 20) - media) / desviacion)))
        c += 20
    x2 = 0
    print("Valor chi cuadrados:")
    for i in range(len(observado)):
        x1 = (((observado[i] - esperado[i]) ** 2) / esperado[i])
        x2 += x1
        print(x2)

    print("Normal")
    print("Observado")
    print(observado)
    print("Esperado")
    print(esperado)
    print("Valor de X2 obtenido = " + str(x2))
    print("Se poseen 10 intervalos, por lo tantos tendremos 9 grados de libertad.")
    print("Con 9 grados de libertad y con un 95 porciento de confianza se obtiene un valor de Chi cuadrado de 16.92")
    if x2 < chiquadesperado:
        print("El valor de chi cuadrado obtenido: " + str(x2) +
              " es menor que " + str(chiquadesperado) + " ,por lo tanto Paso el test")
    else:
        print("No paso el test")


def TestChiCuadPoisson(u):
    """Test de bondad Chi Cuadrado para distribucion Poisson"""
    observado = []
    esperado = []
    X = scipy.stats.poisson(50)
    chiquadesperado = round(scipy.stats.chi2.ppf(1-0.05, 9), 2)
    c = 26
    for i in range(10):
        x = 0
        for j in range(len(u)):
            if (c-6) <= float(u[j]) < c:
                x += 1
        observado.append(x)
        total = sum(X.pmf(k) for k in range(c)) - sum(X.pmf(m) for m in range(c-6))
        esperado.append(1000*total)
        c += 6
    x2 = 0
    print("Valor chi cuadrados:")
    for i in range(len(observado)):
        x1 = (((observado[i]-esperado[i])**2)/esperado[i])
        x2 += x1
        print(x2)

    print("Poisson")
    print("Observado")
    print(observado)
    print("Esperado")
    print(esperado)
    print("Valor de X2 obtenido = " + str(x2))
    print("Se poseen 30 intervalos, por lo tantos tendremos 29 grados de libertad.")
    print("Con 29 grados de libertad y con un 95 porciento de confianza se obtiene un valor de Chi cuadrado de 42,56")
    if x2 < chiquadesperado:
        print("El valor de chi cuadrado obtenido: "+str(x2) +
              " es menor que "+str(chiquadesperado)+" ,por lo tanto Paso el test")
    else:
        print("No paso el test")


def TestChiCuadBinomial(u):
    """Test de bondad Chi Cuadrado para distribucion Binomial"""
    observado = []
    esperado = []
    X = scipy.stats.binom(1000, 0.4)
    c = 354
    chiquadesperado = round(scipy.stats.chi2.ppf(1-0.05, 9), 2)
    for i in range(10):
        x = 0
        for j in range(len(u)):
            if (c-14) <= float(u[j]) < c:
                x += 1
        observado.append(x)
        total = sum(X.pmf(k) for k in range(c)) - sum(X.pmf(m) for m in range (c-14))
        esperado.append(1000*total)
        c += 14
    x2 = 0
    print("Valor chi cuadrados")
    for i in range(len(observado)):
        x1 = (((observado[i]-esperado[i])**2)/esperado[i])
        x2 += x1
        print(x2)

    print("Binomial")
    print("Observado")
    print(observado)
    print("Esperado")
    print(esperado)
    print("Valor de X2 obtenido = " + str(x2))
    print("Se poseen 10 intervalos, por lo tantos tendremos 9 grados de libertad.")
    print("Con 9 grados de libertad y con un 95 porciento de confianza se obtiene un valor de Chi cuadrado de 16.92")
    if x2 < chiquadesperado:
        print("El valor de chi cuadrado obtenido: "+str(x2) +
              " es menor que "+str(chiquadesperado)+" ,por lo tanto Paso el test")
    else:
        print("No paso el test")


def TestChiCuadEmpirica(u):
    """Test de bondad Chi Cuadrado para distribucion Empirica"""
    observado = []
    esperado = []
    chiquadesperado = round(scipy.stats.chi2.ppf(1 - 0.05, 9), 2)
    p = [0.273, 0.037, 0.195, 0.009, 0.124, 0.058, 0.062, 0.151, 0.047, 0.044]
    for i in range(10):
        x = 0
        for j in range(len(u)):
            if u[j] == i + 1:
                x += 1
        observado.append(x)
        esperado.append(1000 * p[i])
    x2 = 0
    print("Valor chi cuadrados:")
    for i in range(len(observado)):
        x1 = (((observado[i] - esperado[i]) ** 2) / esperado[i])
        x2 += x1
        print(x2)

    print("Empírica")
    print("Observado")
    print(observado)
    print("Esperado")
    print(esperado)
    print("Valor de X2 obtenido = " + str(x2))
    print("Se poseen 10 intervalos, por lo tantos tendremos 9 grados de libertad.")
    print(
        "Con 9 grados de libertad y con un 95 porciento de confianza se obtiene un valor de Chi cuadrado de 16.92")
    if x2 < chiquadesperado:
        print("El valor de chi cuadrado obtenido: " + str(x2) +
              " es menor que " + str(chiquadesperado) + " ,por lo tanto Paso el test")
    else:
        print("No paso el test")


def graficar(u, g, e, n, p, b, em, pas, hipergeo):
    plt.figure(1)
    plt.title("Distribución Uniforme")
    plt.hist(u)

    plt.show()

    plt.figure(2)
    plt.title("Distribución Gamma")
    plt.hist(g, 25, histtype="stepfilled", alpha=.7, linewidth=5, color='r')
    plt.show()

    plt.figure(3)
    plt.title("Distribución Exponencial")
    plt.hist(e, 25, histtype="stepfilled", alpha=.7, linewidth=5, color='g')
    plt.show()

    plt.figure(4)
    plt.title("Distribución Normal")
    plt.hist(n, 25, histtype="stepfilled", alpha=.7, linewidth=5, color='y')
    plt.show()

    plt.figure(5)
    plt.title("Distribución Poisson")
    plt.hist(p, 25, histtype="stepfilled", alpha=.7, linewidth=5, color='orange')
    plt.show()

    plt.figure(6)
    plt.title("Distribución Binomial")
    plt.hist(b, 25, histtype="stepfilled", alpha=.7, linewidth=5, color='black')
    plt.show()

    plt.figure(7)
    plt.title("Distribución Empirica")
    plt.hist(em, color='violet')
    plt.show()

    plt.figure(8)
    plt.title("Distribución Pascal")
    plt.hist(pas, color='cyan')
    plt.show()

    plt.figure(9)
    plt.title("Distribución Hipergeometrica")
    plt.hist(hipergeo, 25, histtype="stepfilled", alpha=.7, linewidth=5, color='chocolate')
    plt.show()


def main():
    uni = []
    gam = []
    expo = []
    nor = []
    poi = []
    bino = []
    empi = []
    pas = []
    hipergeo = []

    uni = (uniforme(0, 5, 1000))
    gam = (gamma(5, 20, 1000))
    expo = (exponencial(5, 1000))
    nor = normal(2.35, 30, 1000)
    poi = poisson(50, 1000)
    bino = binomial(1000, 0.4, 1000)
    empi = empirica_discreta(1000)
    pas = pascal(5, 0.4, 1000)
    hipergeo = hipergeometrica(5000000, 500, 0.4, 1000)
    graficar(uni, gam, expo, nor, poi, bino, empi, pas, hipergeo)

    TestChiCuadUni(uni)
    print()
    TestChiCuadExp(expo)
    print()
    TestChiCuadNormal(nor)
    print()
    TestChiCuadBinomial(bino)
    print()
    TestChiCuadPoisson(poi)
    print()
    TestChiCuadEmpirica(empi)


if __name__ == '__main__':
    main()
