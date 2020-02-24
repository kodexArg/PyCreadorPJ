import constantes as ct
import os
import pandas as pd
import numpy as np
import json
import random
from collections import OrderedDict
import pdb


def randomizar_caracteristicas(caracter):
    chances = ct.POSIBILIDAD_TRAIT
    with open(os.path.join(ct.STATIC_ROOT, 'caracteristicas.list')) as f:
        lines = [line.strip('\n') for line in f]

    # se peude mejorar, pero ¿lo voy a entender el año que viene?, no, no lo voy a entender
    c = []
    for line in lines:
        c.append(line.split(','))

    caracteristicas = {}
    indice = 0
    for test in c:
        if caracter['sexo'] == "Mujer":
            test = [w.replace('0', 'a') for w in test]
            test = [w.replace('1', 'a') for w in test]
        else:
            test = [w.replace('0', 'o') for w in test]
            test = [w.replace('1', '') for w in test]

        if np.random.randint(1, 10) < chances:
            caracteristicas.update({indice: np.random.choice(test).strip()})
            chances = chances * 0.8
            indice += 1

    if caracter['opt_trait']:
        t = []
        t.append(caracter['opt_trait'])
        for valor in t:
            caracteristicas[len(caracteristicas)] = valor

    return caracteristicas


def randomizar_atributos(caracter):
    c = caracter['clase']
    p = int(caracter['poder'])
    atributos = ct.df_clases[[c]]\
        .apply(lambda x: np.round(x * p * np.random.normal(1, 0.1)), axis=1)\
        .astype(np.int)\
        .clip(upper=10, lower=4)\
        .to_dict()

    return atributos[caracter['clase']]


def randomizar_habilidades(caracter, atributos):
    c = caracter['clase']
    c2 = caracter['clase2']
    if c2 == "Sin especialización":
        c2 = c

    hlist = []

    with open(os.path.join(ct.STATIC_ROOT, 'skills.json'), 'r') as json_file:
        d = json.load(json_file)

    for atribs, habils in d[c].items():
        for habil in habils.items():
            hkey = habil[0]

            habil_primaria = d.get(c,{}).get(atribs,{}).get(habil[0])
            habil_secundaria = d.get(c2,{}).get(atribs,{}).get(habil[0])
            if habil_primaria > habil_secundaria:
                habil = np.random.random_integers(habil_secundaria, habil_primaria)
            else:
                habil = np.random.random_integers(habil_primaria, habil_secundaria)

            h_inicial = habil  # valor
            h_wiggle = int(np.round(np.random.normal(h_inicial, 1)))  # wiggle
            h_valor = h_wiggle + int(atributos[atribs])  # aumento base
            hlist.append([hkey, int(atributos[atribs]),
                          h_inicial, h_wiggle, h_valor])


    df_habilidades = pd.DataFrame(hlist, columns=['HABILIDAD', 'ATR', 'INI', 'WIG', 'VALOR'])
    df_habilidades = df_habilidades[['HABILIDAD', 'VALOR']].set_index('HABILIDAD').sample(n=round((20*(int(caracter['poder'])/40))))

    # print(df_habilidades)
        # .sample(n=round((12*(int(caracter['poder'])/40))))
    # df_habilidades = df_habilidades.sort_values(by=['VALOR'], ascending=False)
    habilidades = df_habilidades.sort_values(by=['VALOR'], ascending=False).to_dict()

    return habilidades['VALOR']


def randomizar_inventario(caracter, habilidades, atributos, caracteristicas):
    inventario = pd.read_json(os.path.join(ct.STATIC_ROOT, 'inventario.json'))
    selection = {}

    # items por HABILIDADES
    hab_pj = list(habilidades.keys())
    for inv in inventario:
        if inv in hab_pj:
            inv_posible = inventario[inv].dropna()
            for item, atr in inv_posible.iteritems():
                if np.random.random() <= (atr[0]*ct.POSIBILIDAD_INVENTARIO):
                    selection.update({item: atr})

    # items por CARACTERISTICAS

    if len(selection) > 1:
        l = list(selection.items())
        np.random.shuffle(l)
        selection = dict(l)

    return selection


def randomizar_dinero(caracter):
    cash = np.random.randint(0, np.int(caracter['poder'])) * 10
    return {'dinero': cash}


def randomizar_nombre(caracter):

    if caracter['sexo'] == 'Mujer':
        nombres = pd.read_csv(os.path.join(
            ct.STATIC_ROOT, 'spanish-names/mujeres.csv'))
    else:
        nombres = pd.read_csv(os.path.join(
            ct.STATIC_ROOT, 'spanish-names/hombres.csv'))

    apellidos = pd.read_csv(os.path.join(
        ct.STATIC_ROOT, 'spanish-names/apellidos.csv'))

    todrop = nombres[nombres['edad_media'] > int(caracter['poder'])].index
    nombres.drop(todrop, inplace=True)
    nombres_max = np.max(nombres[['frec']])

    if caracter['opt_nombre']:
        nombre = str(caracter['opt_nombre'])
    else:
        pruebas = 0
        while pruebas < ct.INTENTOS:
            pruebas += 1
            test = nombres.sample(n=1)
            chances_aceptar = np.float(test['frec'].values[0]/nombres_max)
            if np.random.random() < chances_aceptar:
                break
        nombre = test['nombre'].values[0]

    if caracter['opt_edad']:
        edad = caracter['opt_edad']
    else:
        e = test['edad_media'].values[0]
        if e < 15:
            e = 15 + np.random.randint(0, 10)
        edad = str(int(e))

    if caracter['opt_apellido']:
        apellido = caracter['opt_apellido']
    else:
        pruebas = 0
        while pruebas < ct.INTENTOS:
            pruebas += 1
            test = apellidos.sample(n=1)
            chances_aceptar = np.float(test['frec_pri'].values[0]/nombres_max)
            if np.random.random() < chances_aceptar:
                break
        apellido = test['apellido'].values[0]

    return {'nombre': nombre, 'apellido': apellido, 'edad': edad}


def randomizar_rasgos(caracter, atributos, habilidades):
    with open(os.path.join(ct.STATIC_ROOT, 'rasgos.json'), 'r') as json_file:
        d = json.load(json_file)


    return ""