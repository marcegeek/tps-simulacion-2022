from random import random
import math


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
        x.append(stdx * (sm-6) + ex)
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
            if(random() - p1) > 0:
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

