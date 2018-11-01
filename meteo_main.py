import sys
import os
import datetime
import calendar
import locale

from PyQt5 import QtWidgets, QtGui

from src.meteo_window import Ui_MainWindow
from src.meteo_window_about import Ui_Dialog
import src.meteo_model as meteo_model


locale.setlocale(locale.LC_ALL, '')

script_dir = os.path.dirname(__file__)

IMG_PATH = 'src/res/view/img/'

# Mapeado para las posiciones de los valores meteorológicos en las columnas
# del grid de la vista, dependiendo del día.
POS_LABELS_DIARIOS = {0: [11, 12, 13, 14], 1: [21, 22, 23, 24], 2: [31, 32],
                        3: [41, 42], 4: [51], 5: [61], 6: [71]}

# En el fichero json los valores de las mediciones se muestran en un orden
# concreto de periodos horarios dependiendo del día de la predicción.
# Los valores que nos interesan son los relativos a los periodos horarios que
# hemos definido en las etiquetas del estado del cielo (frameCielo)
# POS_VALORES_HORARIOS guarda las posiciones iniciales a partir de las cuales
# obtenemos los valores que nos interesan.
POS_VALORES_HORARIOS = {0: 3, 1: 3, 2: 1, 3: 1, 4: 0, 5: 0, 6: 0}

# En el fichero json hay valores de mediciones relativos al día entero
# (temperatura mínima y máxima, índice ultravioleta...)
# Este mapeado indica la columna del grid de la vista relativa a cada
# uno de los días.
POS_VALORES_DIARIOS = {0: 0, 1: 4, 2: 8, 3: 10, 4: 12, 5: 13, 6: 14}

poblaciones_filtradas = []

class MeteoCloud_Window(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)

        qss_path = 'src/res/view/meteo_window.qss'
        stylesheet_abs_path = os.path.join(script_dir, qss_path)
        self.setStyleSheet(open(stylesheet_abs_path, 'r').read())

class MeteoCloud_Dialog_About(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self)

def init_dias(prediccion):
    # Las etiquetas del día están nombradas como labelDia1, labelDia2...
    label_dia_name = 'labelDia'

    for i in range(0, 7):
        d = prediccion['dia'][i]['fecha'].split('-')
        curday = datetime.date(int(d[0]), int(d[1]), int(d[2]))
        # Busca la etiqueta del día correspondiente utilizando
        # el índice del bucle
        curlabel = meteowindow.findChild(QtWidgets.QLabel,
                                        label_dia_name + str(i+1))
        curlabel.setText(curday.strftime('%A %d').title())

def init_cielos_estado(prediccion):
    """Inicializa los distintos estados del cielo con sus respectivas imágenes.

    En los dos primeros días de la predicción, las franjas nocturnas
    (00-06h, 18-24h) pueden tener códigos que correspondan a archivos de
    imagen no existentes.
    Un ejemplo es el estado del cielo Cubierto con tormenta, de código 54.
    En las franjas nocturnas que tengan dicho estado su código es 54n, pero
    AEMET no tiene definida una imagen para ese código en particular.
    Dos soluciones son asignar las imágenes diurnas para esos estados o crear
    nuevas imágenes que los representen, pero al no estar documentadas desde
    AEMET la primera opción es preferible.
    http://www.aemet.es/es/eltiempo/prediccion/municipios/ayuda
    """
    # Las etiquetas de los estados del cielo por periodos horarios están
    # nombradas como labelCielo11, labelCielo12, labelCielo21...
    # Los números de dichos nombres corresponden a los días mapeados en el
    # valor POS_LABELS_DIARIOS
    label_cielo_name = 'labelCielo'

    for i in range(0, 7):
        pos = 0
        for j in POS_LABELS_DIARIOS[i]:
            cielodato = prediccion['dia'][i]['estadoCielo']
            if len(cielodato) > 0:
                cielo = cielodato[POS_VALORES_HORARIOS[i] + pos]['value']
                cielodescripcion = cielodato[POS_VALORES_HORARIOS[i] + pos]['descripcion']
                cielofilepath = IMG_PATH + str(cielo) + '.png'

                if not os.path.isfile(cielofilepath):
                    if i < 2 and (pos == 0 or pos == 3):
                        cielofilepath = IMG_PATH + str(cielo).strip('n') + '.png'
                        if not os.path.isfile(cielofilepath):
                            cielofilepath = IMG_PATH + 'unknown.png'
                    else:
                        cielofilepath = IMG_PATH + 'unknown.png'

                if not cielodescripcion:
                    cielodescripcion = 'Estado de cielo no disponible'

                curlabel = meteowindow.findChild(QtWidgets.QLabel,
                                                label_cielo_name + str(j))
                curlabel.setPixmap(QtGui.QPixmap(cielofilepath))
                curlabel.setToolTip(cielodescripcion)
                pos += 1

def init_cielos_temp(prediccion):
    # Las etiquetas de la temperatura por periodos horarios están nombradas
    # como labelTemp11, labelTemp12, labelTemp21...
    # Los números de dichos nombres corresponden a los días mapeados en el
    # valor POS_LABELS_DIARIOS
    label_temp_name = 'labelTemp'

    for i in range(0, 7):
        pos = 0
        for j in POS_LABELS_DIARIOS[i]:
            tempdato = prediccion['dia'][i]['temperatura']['dato']
            if len(tempdato) > 0:
                temp = tempdato[pos]['value']
                curlabel = meteowindow.findChild(QtWidgets.QLabel,
                                                label_temp_name + str(j))
                curlabel.setText(str(temp) + "ºC")
                pos += 1

def init_precipitaciones(prediccion):
    # Las etiquetas de la precipitación por periodos horarios están nombradas
    # como labelPrecip11, labelPrecip12, labelPrecip21...
    # Los números de dichos nombres corresponden a los días mapeados en el
    # valor POS_LABELS_DIARIOS
    label_precip_name = 'labelPrecip'

    for i in range(0, 7):
        pos = 0
        for j in POS_LABELS_DIARIOS[i]:
            precipdato = prediccion['dia'][i]['probPrecipitacion']
            if len(precipdato) > 0:
                precip = precipdato[POS_VALORES_HORARIOS[i] + pos]['value']
                curlabel = meteowindow.findChild(QtWidgets.QLabel,
                                                label_precip_name + str(j))
                curlabel.setText(str(precip) + "%")
                pos += 1

def init_cota(prediccion):
    # Las etiquetas de la cota de nieve por periodos horarios están nombradas
    # como labelCota11, labelCota12, labelCota21...
    # Los números de dichos nombres corresponden a los días mapeados en el
    # valor POS_LABELS_DIARIOS
    label_cota_name = 'labelCota'

    for i in range(0, 7):
        pos = 0
        for j in POS_LABELS_DIARIOS[i]:
            cotadato = prediccion['dia'][i]['cotaNieveProv']
            if len(cotadato) > 0:
                cota = cotadato[POS_VALORES_HORARIOS[i] + pos]['value']
                curlabel = meteowindow.findChild(QtWidgets.QLabel,
                                                label_cota_name + str(j))
                curlabel.setText(str(cota))
                pos += 1

def init_minmax(prediccion):
    # Las etiquetas de la temperatura mínima / máxima de cada día están
    # nombradas como labelMinMax1, labelMinMax2...
    label_minmax_name = 'labelMinMax'

    for i in range(0, 7):
        tempmin = prediccion['dia'][i]['temperatura']['minima']
        tempmax = prediccion['dia'][i]['temperatura']['maxima']
        curlabel = meteowindow.findChild(QtWidgets.QLabel,
                                        label_minmax_name + str(i+1))
        curlabel.setText(str(tempmin) + " / " + str(tempmax))

def init_viento(prediccion):
    # Las etiquetas del viento por periodos horarios están nombradas como
    # labelViento11, labelViento12, labelViento21...
    # Los números de dichos nombres corresponden a los días mapeados en el
    # valor POS_LABELS_DIARIOS
    label_viento_name = 'labelViento'

    for i in range(0, 7):
        pos = 0
        for j in POS_LABELS_DIARIOS[i]:
            vientodato = prediccion['dia'][i]['viento']
            if len(vientodato) > 0:
                velviento = vientodato[POS_VALORES_HORARIOS[i] + pos]['velocidad']

                dirviento = vientodato[POS_VALORES_HORARIOS[i] + pos]['direccion']
                curlabel = meteowindow.findChild(QtWidgets.QLabel,
                    label_viento_name + str(j))
                curlabel.setText(str(velviento) + " " + dirviento)
                pos += 1

def init_uv(prediccion):
    # Las etiquetas del índice ultravioleta de cada día están nombradas como
    # labelUv1, labelUv2...
    label_uv_name = 'labelUv'

    for i in range(0, 7):
        curlabel = meteowindow.findChild(QtWidgets.QLabel,
                                        label_uv_name + str(i+1))

        if 'uvMax' in prediccion['dia'][i]:
            uv = prediccion['dia'][i]['uvMax']
            curlabel.setText(str(uv))
        else:
            curlabel.setText('')

def hide_columns(prediccion):
    """Oculta en la vista las columnas de las horas pasadas del día actual.

    Los datos que devuelve la API dejan de ser significativos para las horas
    ya pasadas, así que se deben ocultar las columnas designadas a dichas horas.
    """
    dia_actual = datetime.datetime.now().date()
    hora_actual = datetime.datetime.now().time().hour

    d = prediccion['dia'][0]['fecha'].split('-')
    dia_primera_prediccion = datetime.date(int(d[0]), int(d[1]), int(d[2]))

    frame_cielo_name = 'frameCielo'
    label_precip_name = 'labelPrecip'
    label_cota_name = 'labelCota'
    label_viento_name = 'labelViento'

    index = 0
    if ((dia_actual - dia_primera_prediccion).days > 0):
        # Si ya estamos en el día siguiente y la predicción sigue teniendo datos del día anterior.
        index = 4
        meteowindow.findChild(QtWidgets.QLabel, 'labelDia1').hide()
        meteowindow.findChild(QtWidgets.QLabel, 'labelMinMax1').hide()
        meteowindow.findChild(QtWidgets.QLabel, 'labelUv1').hide()
    else:
        # Si estamos en el mismo día que la primera predicción pero ya han pasado tandas de 6 horas.
        index = hora_actual // 6

    for i in range(0, index):
        meteowindow.findChild(QtWidgets.QFrame, frame_cielo_name +
                                str(POS_LABELS_DIARIOS[0][i])).hide()
        meteowindow.findChild(QtWidgets.QLabel, label_precip_name +
                                str(POS_LABELS_DIARIOS[0][i])).hide()
        meteowindow.findChild(QtWidgets.QLabel, label_cota_name +
                                str(POS_LABELS_DIARIOS[0][i])).hide()
        meteowindow.findChild(QtWidgets.QLabel, label_viento_name +
                                str(POS_LABELS_DIARIOS[0][i])).hide()

def init_values():
    """Inicializa cada uno de los apartados de la predicción meteorológica.

    Para la población actual, muestra su nombre, los días que cubre dicha
    predicción, el estado del cielo, las probabilidades de precipitación,
    la cota de nieve, la temperatura mínima y máxima, la velocidad y
    dirección del viento y el índice ultravioleta.
    """
    meteowindow.findChild(QtWidgets.QLabel, 'labelPoblacion').setText(meteo_model.get_nombre_poblacion_seleccionada())
    init_dias(prediccion)
    init_cielos_estado(prediccion)
    init_cielos_temp(prediccion)
    init_precipitaciones(prediccion)
    init_cota(prediccion)
    init_minmax(prediccion)
    init_viento(prediccion)
    init_uv(prediccion)

    hide_columns(prediccion)

def filtrar_poblacion(texto):
    """Filtra la lista de poblaciones según el texto introducido.

    Ignorando mayúsculas, tildes y eñes, busca dicho texto desde el inicio de
    cada una de las palabras contenidas en el nombre de cada población.
    """
    global poblaciones_filtradas

    poblaciones_filtradas.clear()
    vaciar_lista()

    pobs = meteo_model.filter_poblacion(texto)

    filtro_lista = meteowindow.findChild(QtWidgets.QListWidget, 'listWidgetFiltro')
    for codigo, poblacion in pobs.items():
        poblaciones_filtradas.append({codigo: poblacion})
        filtro_lista.addItem(poblacion)

def change_prediccion():
    """Cambia la predicción de población a mostrar.

    Responde a la selección de población filtrada en la lista.
    """
    global prediccion

    filtro_lista = meteowindow.findChild(QtWidgets.QListWidget, 'listWidgetFiltro')

    if (filtro_lista.count() > 0):
        poblacion_seleccionada = poblaciones_filtradas[filtro_lista.currentRow()]
        prediccion = meteo_model.get_prediccion([*poblacion_seleccionada][0])

        init_values()

    boton_favorita = meteowindow.findChild(QtWidgets.QPushButton, 'pushButtonPoblacion')
    boton_favorita.setEnabled(True)

def init_layout():
    """Inicializa las funcionalidades de los distintos elementos interactivos.

    Para filtrar las poblaciones, responde al clic en el botón de filtrar y a
    la pulsación en la tecla Enter mientras se está escribiendo en el campo de
    texto del filtro de población.
    Para la selección de población filtrada, responde al clic y a la pulsación
    de la tecla Enter en un elemento de la lista.
    """
    # Filtrar población
    filtro_lineedit = meteowindow.findChild(QtWidgets.QLineEdit, 'lineEditFiltro')
    filtro_button = meteowindow.findChild(QtWidgets.QPushButton, 'pushButtonFiltro')
    filtro_lineedit.returnPressed.connect(lambda: filtrar_poblacion(filtro_lineedit.text()))
    filtro_button.clicked.connect(lambda: filtrar_poblacion(filtro_lineedit.text()))

    # Mostrar población seleccionada
    vaciar_lista()
    filtro_lista = meteowindow.findChild(QtWidgets.QListWidget, 'listWidgetFiltro')
    filtro_lista.itemActivated.connect(lambda: change_prediccion())
    filtro_lista.itemClicked.connect(lambda: change_prediccion())

    # Establecer población actual como favorita
    boton_favorita = meteowindow.findChild(QtWidgets.QPushButton, 'pushButtonPoblacion')
    boton_favorita.clicked.connect(lambda: poblacion_favorita());

    # Menús
    menu_salir = meteowindow.findChild(QtWidgets.QAction, 'actionSalir')
    menu_salir.triggered.connect(lambda: sys.exit())

    menu_acerca = meteowindow.findChild(QtWidgets.QAction, 'actionAcerca_de')
    menu_acerca.triggered.connect(lambda: show_about_dialog())

def poblacion_favorita():
    boton_favorita = meteowindow.findChild(QtWidgets.QPushButton, 'pushButtonPoblacion')
    boton_favorita.setEnabled(False)

    meteo_model.set_poblacion_favorita()

def show_about_dialog():
    global meteowindow_about

    meteowindow_about = MeteoCloud_Dialog_About()
    meteowindow_about.exec_()

def vaciar_lista():
    filtro_lista = meteowindow.findChild(QtWidgets.QListWidget, 'listWidgetFiltro')
    filtro_lista.clear()

def init_model():
    global prediccion

    meteo_model.get_api_key()
    meteo_model.load_poblaciones()
    meteo_model.load_poblacion_favorita()
    prediccion = meteo_model.get_prediccion()

if __name__ == "__main__":

    init_model()

    app = QtWidgets.QApplication(sys.argv)
    meteowindow = MeteoCloud_Window()
    meteowindow.show()

    #print(meteowindow.findChild(QtWidgets.QLabel, "labelMinMax").text())
    #print(meteowindow.framePrediccion.layout().itemAtPosition(0, 0).widget().text())
    #meteowindow.findChild(QtWidgets.QFrame, 'frameCielo11').hide()

    init_values()
    init_layout()

    sys.exit(app.exec_())
