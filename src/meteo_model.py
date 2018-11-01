import requests
import json
import os
import re

import unidecode

script_dir = os.path.dirname(__file__)

url = 'https://opendata.aemet.es/opendata/api/prediccion/especifica/municipio/diaria/'

headers = {'Accept': 'application/json',
'api_key': ''}

poblacion_favorita = 28079

poblacion_seleccionada = 0

poblaciones = [{}]

poblaciones_filtro = [{}]

def get_api_key():
    """Obtiene la clave de API de su fichero en la carpeta res. """
    api_path = os.path.join(script_dir, 'res/api_key.txt')

    if os.path.isfile(api_path):
        api_file = open(api_path, 'r')
        try:
            headers['api_key'] = api_file.read()
        finally:
            api_file.close()

    else:
        print('Archivo de API no encontrado. Tiene que existir un archivo ' +
        'llamado api_key.txt dentro de la carpeta /res/ que contenga la clave' +
        ' de API de AEMET OpenData.')

def load_poblaciones():
    """Carga el archivo con la lista de poblaciones y sus identificadores. """
    global poblaciones

    poblaciones_path = 'res/poblaciones.json'
    poblaciones_abs_path = os.path.join(script_dir, poblaciones_path)

    with open(poblaciones_abs_path, 'r') as jsonf:
        poblaciones = json.load(jsonf)
        print(str(len(poblaciones[0])))

def load_poblacion_favorita():
    """Carga la población favorita guardada en la carpeta /res/, si existe. """
    global poblacion_favorita, poblacion_seleccionada

    favorita_path = 'res/poblacion_favorita.txt'
    favorita_abs_path = os.path.join(script_dir, favorita_path)

    if os.path.isfile(favorita_abs_path):
        with open(favorita_abs_path, 'r') as fav:
            pob_leida = fav.readline()
            if pob_leida.isdigit():
                poblacion_favorita = pob_leida

def set_poblacion_favorita():
    favorita_path = 'res/poblacion_favorita.txt'
    favorita_abs_path = os.path.join(script_dir, favorita_path)

    with open(favorita_abs_path, 'w+') as fav:
        fav.write(str(poblacion_seleccionada))

def filter_poblacion(filtro):
    """Filtra la lista de poblaciones con el texto introducido.

    Comprueba si cada población contiene el texto introducido desde el inicio
    de cualquier palabra que contenga en su nombre, ignorando mayúsculas,
    tildes y eñes.
    """
    global poblaciones_filtro

    poblaciones_filtro[0].clear()

    filtro_unidec = unidecode.unidecode(filtro)
    patron = re.compile(r'\b({0})'.format(filtro_unidec), flags=re.IGNORECASE)

    for k, v in poblaciones[0].items():
        if patron.search(unidecode.unidecode(v)):
            poblaciones_filtro[0][k] = v

    print('Resultados: ' + str(len(poblaciones_filtro[0])))
    return poblaciones_filtro[0]

def get_nombre_poblacion_seleccionada():
    """Obtiene el nombre de la población seleccionada. """
    return poblaciones[0][str(poblacion_seleccionada)]

def get_prediccion(poblacion_actual = None):
    """Devuelve la predicción de la población pasada por parámetro. """
    global poblacion_seleccionada

    if poblacion_actual is None:
        poblacion_seleccionada = poblacion_favorita
    else:
        poblacion_seleccionada = poblacion_actual

    r = requests.get(url + str(poblacion_seleccionada), headers=headers)

    data = r.json()

    prediccion = {}

    if data['estado'] == 200:
        print('Good to go')
        localidad = requests.get(data['datos']).json()

        prediccion = localidad[0]['prediccion']
    else:
        print('Error ' + str(data['estado']) + '.')
        if data['estado'] == 401:
            print('Acceso no autorizado, necesitas una clave de API válida' +
            ' en el archivo api_key.txt')
        elif data['estado'] == 404:
            print('Población inexistente.')
        elif data['estado'] == 429:
            print('Demasiadas peticiones.')
        else:
            print('Error no documentado.')

    return prediccion

if __name__ == "__main__":
    get_api_key()
    load_poblaciones()
    get_prediccion()
    filter_poblacion('corun')
