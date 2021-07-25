# -*- coding: utf-8 -*-
"""
Suicide Burn with PID calculations

- Kerbal Space Program (tested on 1.12.1.3142)
- kRPC mod (tested on 0.4.8)
- tested on Python 3.9 https://www.python.org/ (2.7 should also work)
- Developed by Andrey Hertel and Maurício Mazur

"""
import krpc
import pygame
import sys
import os

import controlePID

specialVariable = 10

'''
IMPORTANT INFO:
In order for the code to know when to start burning fuel at the correct time and 
to accurately bring the ship to the ground, it needs to know the distance to the 
surface below it, but the only information we can get is the distance from the cockpit 
(or the probe computer) to the surface. The variable 'specialVariable' above must be changed based on the 
distance from the landing gear to the cockpit.
I've tested 2 crafts: The 1st one had it's cockpit 2m above the ground and a number 7 on that variable did the trick, 
the 2nd one had it's cockpit 2.7m above the ground and a number 10 on that variable did the trick, I know that
it has a logic, but I'm too lazy right now to figure it out. XD

You may also increase it to make your rocket hover and start decreasing it gradually until it lands 
(I'll implement it later)

'''

# Pygame constants
pygame.init()

telaWidth = 1024
telaHeight = 768
tela = pygame.display.set_mode((telaWidth, telaHeight))
pygame.display.set_caption('KSP Suicide Burn by Andrey Hertel')
font = pygame.font.SysFont('arial', 23)
font2 = pygame.font.SysFont('arial', 100)

# kRPC constants
nome = 'Suicide Burn'
conn = krpc.connect(nome)
ksp = conn.space_center
vessel = ksp.active_vessel
engine = ksp.Engine
body = vessel.orbit.body
flight = vessel.flight(body.reference_frame)
controle = vessel.control
nomeCorpoCeleste = body.name

# info variables
surAlt = conn.add_stream(getattr, flight, 'surface_altitude')
horizontal = conn.add_stream(getattr, flight, 'horizontal_speed')
vertical = conn.add_stream(getattr, flight, 'vertical_speed')
thrust_max = conn.add_stream(getattr, vessel, 'max_thrust')
massa = conn.add_stream(getattr, vessel, 'mass')
gravidade = conn.add_stream(getattr, body, 'surface_gravity')
velocidade = conn.add_stream(getattr, flight, 'speed')
situacao = conn.add_stream(getattr, vessel, 'situation')
# time
UT = conn.add_stream(getattr, ksp, 'ut')
pouso = False
pousado_agua = conn.space_center.VesselSituation.splashed
pousado = conn.space_center.VesselSituation.landed
prelancamento = conn.space_center.VesselSituation.pre_launch
distanciaDaQueima = 0
distanciaPouso = specialVariable
TWRMax = 0
landingGearAlt = 500

# Pygame assets
icon = pygame.image.load(os.path.join("Assets", "321.png")).convert_alpha()
pygame.display.set_icon(icon)

fogueteImgRaw = pygame.image.load(os.path.join("Assets", "rocket.png")).convert_alpha()
fogueteImg = pygame.transform.scale(fogueteImgRaw, (200, 200))
munImgRaw = pygame.image.load(os.path.join("Assets", "black.jpg")).convert()
munImg = pygame.transform.scale(munImgRaw, (telaWidth, telaHeight))
kerbinImgRaw = pygame.image.load(os.path.join("Assets", "black.jpg")).convert()
kerbinImg = pygame.transform.scale(kerbinImgRaw, (telaWidth, telaHeight))


# Variables Updater
def atualizarvariaveis():
    global TWRMax
    TWRMax = thrust_max() / (massa() * gravidade())
    acelMax = (TWRMax * gravidade()) - gravidade()
    tempoDaQueima = velocidade() / acelMax
    global distanciaDaQueima
    distanciaDaQueima = velocidade() * tempoDaQueima + 1 / 2 * acelMax * (tempoDaQueima ** 2)
    return TWRMax, acelMax, tempoDaQueima, distanciaDaQueima


class SuicideBurn:
    @staticmethod
    def suicide():
        global pouso
        global distanciaDaQueima
        global TWRMax
        global specialVariable

        rodando = True
        clock = pygame.time.Clock()

        if situacao == pousado or situacao == pousado_agua:
            pouso = False
        while pouso is False or rodando is True:
            # defining PID valors
            PID = controlePID.ControladorPID(0.021, 0.001, 1, UT(),
                                             UT())  # <================================= PID adjustments
            global distanciaDaQueima
            global distanciaPouso
            atualizarvariaveis()
            PID.setValorEntrada(surAlt())
            PID.setValorLimite(distanciaPouso + distanciaDaQueima)
            PID.setLimiteSaida(-1, 1)
            atualizarvariaveis()

            # Examinations
            #  <============================================================== SAS Constrol
            controle.sas = True
            if horizontal() > 2 and surAlt() > 1000:
                controle.sas_mode = controle.sas_mode.retrograde

            if horizontal() > 2 and surAlt() <= (distanciaPouso + 50):
                controle.sas_mode = controle.sas_mode.retrograde
            # elif horizontal() < 2 and surAlt() <= distanciaPouso:
            #    controle.sas_mode = controle.sas_mode.radial

            if surAlt() < landingGearAlt:  # <=========================== landing gear
                controle.gear = True
            else:
                controle.gear = False
            controle.brakes = True

            # update
            atualizarvariaveis()
            correcao = PID.saidaPID(UT(), 0.019)

            # Print info
            print("TWR  : " + "%.4s" % str(TWRMax),
                  "      |      Dist. Burn  : " + "%.6s" % str(distanciaDaQueima),
                  "      |      Altitude  : " + "%.8s" % str(surAlt()),
                  "      |      Correction  : " + "%.4s" % str(correcao))

            # PID.saidaPID(UT(), 0.025)

            if TWRMax == 0:
                TWRMax = 0.0000001


            novaAcel = (1 / TWRMax + correcao)  # <----------------------------------------- acceleration calculations

            # if landed cut power
            if (situacao() == pousado or situacao() == pousado_agua) and int(horizontal()) <= 1:
                controle.throttle = 0
                pouso = True
            else:
                controle.throttle = novaAcel
            # time.sleep(0.2)

            # Pygame stuff
            for i in pygame.event.get():
                if i.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            tela.fill((255, 255, 255))

            if nomeCorpoCeleste == "Mun":
                tela.blit(munImg, (0, 0))
            elif nomeCorpoCeleste == "Kerbin":
                tela.blit(kerbinImg, (0, 0))

            TextX = 0
            TextY = 0
            TextYfollow = ((surAlt() * -1) + telaHeight) - 300

            if TextYfollow < 0:
                TextYfollow = 0

            surAltTxt = font.render('Altitude: ' + "%.5s" % str(surAlt()) + "m", False,
                                    (255, 255, 255))
            nivelMotor = font.render('Engines at: ' + '%.3s' % str(controle.throttle * 100) + '%', False,
                                     (255, 255, 255))
            twrTxt = font.render("TWR  : " + "%.4s" % str(TWRMax), False,
                                 (255, 255, 255))
            correctTxt = font.render("Correction  : " + "%.4s" % str(correcao), False,
                                     (255, 255, 255))
            surface = font.render('     Landing on: ' + nomeCorpoCeleste, False,
                                  (255, 255, 255))
            landedTxt = font2.render(' LANDED', False, (50, 255, 50))

            if controle.gear is False:
                gear = "AUTO-DEPLOYING LANDING GEAR IN " + "%.5s" % str((surAlt() - landingGearAlt)) + "m"
                gearColor = (255, 50, 50)
            else:
                gear = "           LANDING GEAR DEPLOYED"
                gearColor = (50, 255, 50)

            gearTxt = font.render(gear, False, gearColor)

            if TWRMax == 0.0000001:
                debug = font2.render('NO ENGINES ACTIVE', False, (255, 55, 55))
                tela.blit(debug, (0, 250))
                print('NO ENGINES ACTIVE')

            tela.blit(fogueteImg, (420, (((surAlt() // 3) * -1) + telaHeight) - 303))
            tela.blit(surAltTxt, (TextX + 50, TextYfollow))
            tela.blit(nivelMotor, (TextX + 50, TextYfollow + 50))
            tela.blit(twrTxt, (TextX + 50, TextYfollow + 100))
            tela.blit(correctTxt, (TextX + 50, TextYfollow + 150))
            tela.blit(gearTxt, (TextX + 300, TextY))
            tela.blit(surface, (400, 667))
            pygame.draw.line(munImg, (255, 255, 255), (0, 665), (1024, 665), 3)

            if pouso:
                tela.blit(landedTxt, (TextX + 300, TextY + 250))

            pygame.display.update()
            clock.tick(60)


suicideBurn = SuicideBurn()

'''
if situacao() == pousado or situacao() == prelancamento:
    teste = surAlt() - 50
    while teste < distanciaPouso:
        teste = surAlt() - 55
        print("Subindo...")
        controle.gear = False
        atualizarvariaveis()
        controle.throttle = (float(1 / TWRMax * 1.5))
'''

controle.throttle = 0
suicideBurn.suicide()
