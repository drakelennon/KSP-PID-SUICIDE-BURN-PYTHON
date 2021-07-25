# -*- coding: utf-8 -*-
"""
========== PID CONTROLLER =================

Suicide Burn com calculos PID

Para rodar é necessario:
- Kerbal Space Program (tested on 1.12.1.3142)
- kRPC mod (tested on 0.4.8)
- tested on Python 3.9 https://www.python.org/ (2.7 should also work)
- Developed by Andrey Hertel and Maurício Mazur

- will be imported by SB.py

"""

universal = 0
valorEntrada = 0
valorLimite = 0
termoInt = 0
saidaMax = 0
saidaMin = 0
valorSaida = 0
ki = 0
ultValorEntrada = 0
kp = 0
kd = 0
tempo = 0
amostraTempo = 0
ultCalculo = 0
mudancaTempo = 0
erro = 0
dvalorEntrada = 0
tempoPassado = 0
agora = 0


class ControladorPID(object):
    def __init__(self, p, i, d, universalinit, tempoinit):
        self.p = p
        self.i = i
        self.d = d
        self.universal = universalinit
        self.tempo = tempoinit
        global kp, ki, kd
        kp = p
        ki = i
        kd = d
        self.valor = 0
        self.minimo = 0
        self.maximo = 0
        self.tempo = 0
        self.hora = 0
        self.amostra = 0

    global tempo, universal, tempoPassado, agora
    global kp, ki, kd  # // PID adjustments PID 0.025, 0.001, 1)
    global valorEntrada, valorSaida, valorLimite  # // variáveis de valores
    global termoInt, ultValorEntrada  # // variáveis de cálculo de erro
    global mudancaTempo, amostraTempo
    global erro
    global dvalorEntrada
    global saidaMin, saidaMax

    def setValorEntrada(self, valor):
        global valorEntrada
        self.valor = valor
        if valor > 0:
            valorEntrada = valor
        return valorEntrada

    def setValorLimite(self, valor):
        global valorLimite
        self.valor = valor
        if valor > 0:
            valorLimite = valor
        return valorLimite

    def setLimiteSaida(self, minimo, maximo):
        self.minimo = minimo
        self.maximo = maximo
        Min = minimo
        Max = maximo
        global termoInt, saidaMax, saidaMin, valorSaida
        if Min > Max:
            return
        saidaMin = Min
        saidaMax = Max

        if termoInt > saidaMax:
            termoInt = saidaMax

        elif termoInt < saidaMin:
            termoInt = saidaMin

        if valorSaida > saidaMax:
            valorSaida = saidaMax

        elif valorSaida < saidaMin:
            valorSaida = saidaMin
        return valorSaida, saidaMax, saidaMin, termoInt

    def setTEmpo(self, tmp):
        self.tempo = tmp

    def saidaPID(self, hour, displaythis):
        self.hora = hour
        self.amostra = displaythis
        global mudancaTempo, erro, valorLimite, valorSaida, valorEntrada, saidaMin, saidaMax, dvalorEntrada, kp
        global termoInt, ultValorEntrada, ki, kd, ultCalculo  # // variáveis de cálculo de erro
        tempoAgr = hour
        tempoPassadoSaida = tempoAgr - 0.025
        momentoAgr = hour  # ; // variável que busca o tempo imediato
        mudancaTempo = momentoAgr - tempoPassadoSaida  # ; // variável que compara o tempo de cálculo
        displayTime = displaythis
        if mudancaTempo >= displayTime:  # {// se a mudança for maior que o tempo de amostra, o cálculo é feito.
            # // variáveis para o cálculo do valor de saída
            erro = valorLimite - valorEntrada
            termoInt += ki * erro
            if termoInt > saidaMax:
                termoInt = saidaMax
            elif termoInt < saidaMin:
                termoInt = saidaMin
            dvalorEntrada = (valorEntrada - ultValorEntrada)
            # // computando o valor de saída
            valorSaida = kp * erro + ki * termoInt - kd * dvalorEntrada
            if valorSaida > saidaMax:
                valorSaida = saidaMax
            elif valorSaida < saidaMin:
                valorSaida = saidaMin
            # // relembrando os valores atuais para a próxima vez
            ultValorEntrada = valorEntrada
            ultCalculo = momentoAgr
        return valorSaida
