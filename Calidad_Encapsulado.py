#!/usr/bin/env python
# coding: utf-8


def llamada_calidad():
    import os
    import tabula
    import pandas as pd
    import numpy as np
    import shutil
    import nums_from_string
    import time
    import logging
    import configparser
    import sys
    from time import strftime
    import logging.handlers
    import logging.config

    # Leer archivo config.ini
    config_obj = configparser.ConfigParser()
    config_file = os.path.join(os.path.dirname(__file__), 'configCalidad.ini')
    config_obj.read(config_file)
    param = config_obj["host"]
    useInfo = config_obj["user_info"]
    rutas = config_obj["rutas"]
    log = config_obj["logData"]
    
    user = param["user"]
    password = param["password"]
    rutaEntrada = rutas["rutaEntrada"]
    rutaSalida = rutas["rutaSalida"]
    rutaArchivoCalidad = rutas["rutaArchivoCalidad"]
    rutaCalidad = rutas["rutaCalidad"]
    centro_bloque = rutas["centro_bloque"]
    log = log["log"]
    
    # CARGA DATAFRAMES Y DICCIONARIOS ####
    pd.options.display.max_columns = None
    dfCentroBloque = pd.read_excel(centro_bloque)
    dfCentroBloque.columns.str.match('Unnamed')
    zip(dfCentroBloque.Centro, dfCentroBloque.Bloque)
    centroBloque = dict(zip(dfCentroBloque.Centro.astype(str), dfCentroBloque.Bloque))
    
    
    def oldlogs():
        """Función que elimina los logs archivados mayores a una fecha definida"
            """
        now = time.time()
    
        for f in os.listdir(log):
            f = os.path.join(log, f)
            if os.stat(f).st_mtime < now - 30 * 86400:
                if os.path.isfile(f):
                    os.remove(f)
    
    
    def logcreate():
        """Función que nos permite tener un seguimiento de lo que el programa va realizando en la gestion" \
                        "de los archivos
        """
        logfile = log+'LogResult {}.log'.format(strftime('%d-%b-%Y  %H_%M_%S'))
        formatstr = " %(asctime)s: (%(filename)s): %(levelname)-8s: %(funcName)s Line: %(lineno)04d - %(message)s"
        datestr = strftime('[%d-%b-%Y  %H_%M_%S]')
    
        # Imprime todos los mensajes
        logging.basicConfig(
            filename=logfile,
            level=logging.DEBUG,
            filemode="w",
            format=formatstr,
            datefmt=datestr
            )
    
    
    def existeono(directorio, file):
        """Función que nos ayuda a filtrar si un archivo se encuentra en la ruta indicada o no.
           Devuelve True o False
        """
        ruta = f'{directorio}{file}'
        if os.path.isfile(ruta):
            print("El archivo " + file + " existe en la ruta indicada")
            return True
        else:
            print("El archivo " + file + " NO existe en la ruta indicada")
            return False
    
    
    def numeroexpediente(listaarchivos):
        """Sencilla función que extrae el número de expediente del nombre del archivo
           Devuelve los datos en forma de lista
        """
        expediente = []
        for i in listaarchivos:
            expediente.append(i[9:16])
        return expediente
    
    
    def numerocode(rutapdf):
        """Función que extrae el código de tienda encontrado dentro del PDF
           Devuelve los datos en forma de lista
        """
        codigotienda = []
        for i in rutapdf:
            pdf = tabula.read_pdf(i, output_format="json", pages='1')
            tien = pdf[1]["data"][3][0]["text"][0:4]  # MD STORE
            codigotienda.append(tien)
        return codigotienda
    
    
    def tienesp(rutaespanol, archivoespanol, destinoarchivo):
        """función que procesa los PDFs de tiendas españolas, extrayendo la información solicitada y el link
           donde se hospedará el fichero procesado. Posteriormente, mueve el PDF a la carpeta de archivo
           Argumentos:
           rutaespanol: String con la ruta completa donde se encuentra el archivo con tienda española
           archivoespanol: String con el nombre del archivo de tienda española
           destinoarchivo: String con la ruta destino a la que irá a parar el archivo una vez procesado
        """
        print(rutaespanol)
        pdf = tabula.read_pdf(rutaespanol, output_format="json", pages='1')
        logging.info('Procesando archivo: ' + archivoespanol)
        fech = pdf[1]["data"][1][2]["text"][:-9]  # DATE ESPAÑA
        fecha.append(fech)
        pob = pdf[1]["data"][4][1]["text"]  # PLACE
        poblacion.append(pob)
        # LOGISTIC BLOCK
        den = pdf[1]["data"][6][1]["text"]  # PRODUCT
        denominacion.append(den)
        prov = pdf[1]["data"][9][0]["text"]  # SUPPLIER
        proveedor.append(prov)
        desc = pdf[1]["data"][19][0]["text"]  # CAUSE
        descripcion.append(desc)
        lot = pdf[1]["data"][10][1]["text"]  # BATCH
        lote.append(lot)
        lj = pdf[1]["data"][12][1]["text"]  # PACKAGE STATION
        lonja.append(lj)
        nb = pdf[1]["data"][12][0]["text"]  # FISH FARM
        barco.append(nb)
        fe = pdf[1]["data"][13][1]["text"]  # PACKING DAY
        fenvasado.append(fe)
        cadu = pdf[1]["data"][10][3]["text"]  # USE BY
        caducidad.append(cadu)
        ud = pdf[1]["data"][14][3]["text"]  # UNITS CLAIMED
        if ud == 'kg':
            ud = 1
            unid = ud
            unidad.append(unid)
        elif ud == '':
            ud = 0
            unid = ud
            unidad.append(unid)
        else:
            unid = ud.replace(',', '.')
            unida = nums_from_string.get_nums(unid)
            unids = unida[0]
            unidad.append(unids)
            # UNITS ACCEPTED
        lin = r'external:' + destinoarchivo + archivoespanol
        link.append(lin)
        shutil.move(rutaespanol, destinoarchivo + archivoespanol)
        logging.info('PDF ' + archivoespanol + ' procesado y movido a archivo')
    
    
    def tienpor(rutaportugues, archivoportugues, destinoarchivo):
        """función que procesa los PDFs de tiendas portuguesas, extrayendo la información solicitada y el link
           donde se hospedará el fichero procesado. Posteriormente, mueve el PDF a la carpeta de archivo
           Argumentos:
           rutaportugues: String con la ruta completa donde se encuentra el archivo con tienda portuguesa
           archivoportugues: String con el nombre del archivo de tienda portuguesa
           destinoarchivo: String con la ruta destino a la que irá a parar el archivo una vez procesado
        """
        print(rutaportugues)
        pdf = tabula.read_pdf(rutaportugues, output_format="json", pages='1')
        logging.info('Procesando archivo: ' + archivoportugues)
        if pdf[1]["data"][1][1]["text"] == '':
            fech = pdf[1]["data"][1][4]["text"]  # DATE PORTUGAL
            solofecha = fech[:-9]
            fecha.append(solofecha)
        else:
            fech = 'Rellenar datos manualmente'
            fecha.append(fech)
        if pdf[1]["data"][4][1]["text"] == '':
            pob = pdf[1]["data"][4][2]["text"]  # PLACE
            poblacion.append(pob)
        elif pdf[1]["data"][4][2]["text"] == '':
            pob = pdf[1]["data"][4][1]["text"]
            poblacion.append(pob)
        else:
            pob = 'Rellenar datos manualmente'
            poblacion.append(pob)
        # LOGISTIC BLOCK
        if pdf[1]["data"][6][2]["text"] == '':
            den = pdf[1]["data"][6][1]["text"]  # PRODUCT
            denominacion.append(den)
        elif pdf[1]["data"][6][1]["text"] == '':
            den = pdf[1]["data"][6][2]["text"]  # PRODUCT
            denominacion.append(den)
        else:
            den = 'Rellenar datos manualmente'
            denominacion.append(den)
        if pdf[1]["data"][7][1]["text"] == '':
            prov = pdf[1]["data"][7][2]["text"]  # SUPPLIER
            proveedor.append(prov)
        elif pdf[1]["data"][7][2]["text"] == '':
            prov = pdf[1]["data"][7][1]["text"]  # SUPPLIER
            proveedor.append(prov)
        else:
            prov = 'Rellenar datos manualmente'
            proveedor.append(prov)
        if pdf[1]["data"][16][1]["text"] == '':
            desc = pdf[1]["data"][16][2]["text"]  # CAUSE
            descripcion.append(desc)
        elif pdf[1]["data"][16][2]["text"] == '':
            desc = pdf[1]["data"][16][1]["text"]  # CAUSE
            descripcion.append(desc)
        else:
            desc = 'Rellenar datos manualmente'
            descripcion.append(desc)
        if pdf[1]["data"][8][1]["text"] == '':
            lot = pdf[1]["data"][8][2]["text"]  # BATCH
            lote.append(lot)
        elif pdf[1]["data"][8][2]["text"] == '':
            lot = pdf[1]["data"][8][1]["text"]  # BATCH
            lote.append(lot)
        else:
            lot = 'Rellenar datos manualmente'
            lote.append(lot)
        lj = pdf[1]["data"][10][3]["text"]  # PACKAGE STATION
        lonja.append(lj)
        nb = pdf[1]["data"][10][0]["text"]  # FISH FARM
        barco.append(nb)
        if pdf[1]["data"][11][1]["text"] == '':
            fe = pdf[1]["data"][11][2]["text"]  # PACKING DAY
            fenvasado.append(fe)
        elif pdf[1]["data"][11][2]["text"] == '':
            fe = pdf[1]["data"][11][1]["text"]  # PACKING DAY
            fenvasado.append(fe)
        else:
            fe = 'Rellenar datos manualmente'
            fenvasado.append(fe)
        if pdf[1]["data"][8][3]["text"] == 'FECHA CADUCIDAD':
            cadu = 'Rellenar datos manualmente'  # USE BY
            caducidad.append(cadu)
        else:
            cadu = pdf[1]["data"][8][3]["text"]  # USE BY
            caducidad.append(cadu)
        if pdf[1]["data"][12][3]["text"] == 'UNIDADES':
            ud = pdf[1]["data"][12][5]["text"]  # UNITS CLAIMED
            if ud == 'kg':
                ud = 1
                unid = ud
                unidad.append(unid)
            elif ud == '':
                ud = 0
                unid = ud
                unidad.append(unid)
            else:
                unid = ud.replace(',', '.')
                unida = nums_from_string.get_nums(unid)
                unids = unida[0]
                unidad.append(unids)
                # UNITS ACCEPTED
        else:
            ud = pdf[1]["data"][12][3]["text"]
            if ud == 'kg':
                ud = 1
                unid = ud
                unidad.append(unid)
            elif ud == '':
                ud = 0
                unid = ud
                unidad.append(unid)
            else:
                unid = ud.replace(',', '.')
                unida = nums_from_string.get_nums(unid)
                unids = unida[0]
                unidad.append(unids)
                # UNITS ACCEPTED
        lin = r'external:' + destinoarchivo + archivoportugues
        link.append(lin)
        shutil.move(rutaportugues, destinoarchivo + archivoportugues)
        logging.info('PDF ' + archivoportugues + ' procesado y movido a archivo')
    
    
    def creadataframe(dfcalidadhoy, dfcentrobloque, centrobloque):
        """función que recopila toda la información procesada en las funciones que extraen los PDFs, " \
           genera un dataframe y lo exporta a la ruta establecida
           Argumentos:
           dfcalidadhoy: Dataframe que recopila todos los datos extraídos de los PDF
           dfcentrobloque: Dataframe que contiene el centro y el bloque logístico asociado
           centrobloque: Diccionario que asocia cada centro a un bloque logístico
        """
        dfcalidadhoy['DATE'] = fecha
        dfcalidadhoy['EXP'] = exp
        dfcalidadhoy['MD STORE'] = code
        dfcalidadhoy['PLACE'] = poblacion
        listacode = str(dfcentrobloque['Centro'].tolist())
        for i in code:
            if i in listacode:
                dfcalidadhoy['LOGISTIC BLOCK'] = dfcalidadhoy['MD STORE'].astype(str).map(centrobloque)
            else:
                dfcalidadhoy['LOGISTIC BLOCK'][i] = "Tienda No registrada"
        dfcalidadhoy['PRODUCT'] = denominacion
        dfcalidadhoy['SUPPLIER'] = proveedor
        dfcalidadhoy['CAUSE'] = descripcion
        dfcalidadhoy['BATCH'] = lote
        dfcalidadhoy['PACKAGE STATION'] = lonja
        dfcalidadhoy['FISH FARM'] = barco
        dfcalidadhoy['PACKING DAY'] = fenvasado
        dfcalidadhoy['USE BY'] = caducidad
        dfcalidadhoy['UNITS CLAIMED'] = unidad
        dfcalidadhoy['UNITS ACCEPTED'] = pd.DataFrame(columns=['UNITS ACCEPTED'])  # Crea columna COMENTARIOS
        dfcalidadhoy['UNITS ACCEPTED'] = dfcalidadhoy['UNITS ACCEPTED'].replace(np.nan, '',
                                                                                regex=True)  # Elimina los NaN de la columna
        dfcalidadhoy.loc[dfcalidadhoy['UNITS CLAIMED'] <= 3, ['UNITS ACCEPTED']] = dfcalidadhoy['UNITS CLAIMED']
        dfcalidadhoy['UNITS CLAIMED'] = dfcalidadhoy['UNITS CLAIMED'].replace([0], '')
        dfcalidadhoy['UNITS ACCEPTED'] = dfcalidadhoy['UNITS ACCEPTED'].replace([0], '')
        dfcalidadhoy['LINK'] = link
        dfcalidadhoy.to_excel(rutaSalida + " " + filexlsx, index=True)
    
    
    oldlogs()
    
    start_time = time.time()
    timenow = time.strftime("%d-%b-%Y  %H_%M_%S")
    
    listArchNo = [f for f in sorted(os.listdir(rutaEntrada)) if (str(f))[-3:] == "pdf" and existeono(rutaArchivoCalidad,
                                                                                                     f) is False]
    
    
    #  Comprobación de archivos a cargar. Si no hay archivos, termina la ejecución
    if len(listArchNo) == 0:
        sys.exit('No hay datos a procesar')
    
    logcreate()
    
    logging.info('Inicio de la ejecución')
    cuentapdfs = len(listArchNo)
    logging.info('Procesando' + ' ' + str(cuentapdfs) + ' ' +'archivos')
    filexlsx = 'Input Calidad' + " " + timenow + '.xlsx'
    
    fecha, tienda, poblacion, logistic, denominacion, proveedor, descripcion = ([] for i in range(7))
    lote, lonja, barco, fenvasado, caducidad, unidad, unitsacc, link = ([] for j in range(8))
    columnas = ['DATE', 'EXP', 'MD STORE', 'PLACE', 'LOGISTIC BLOCK', 'PRODUCT', 'SUPPLIER', 'CAUSE', 'BATCH',
                'PACKAGE STATION', 'FISH FARM', 'PACKING DAY', 'USE BY', 'UNITS CLAIMED', 'UNITS ACCEPTED', 'LINK']
    
    dfCalidadHoy = pd.DataFrame(columns=columnas)
    listArchNo_with_path = [str(rutaEntrada) + str(f) for f in listArchNo]
    exp = numeroexpediente(listArchNo)
    code = numerocode(listArchNo_with_path)
    
    for i in range(len(listArchNo)):
        if code[i] > '7000' or code[i] == '7000':
            tienpor(listArchNo_with_path[i], listArchNo[i], rutaArchivoCalidad)
        else:
            tienesp(listArchNo_with_path[i], listArchNo[i], rutaArchivoCalidad)
    
    creadataframe(dfCalidadHoy, dfCentroBloque, centroBloque)
    
    tiempoTranscurrido = time.time() - start_time
    totaltime = time.strftime("%H:%M:%S", time.gmtime(tiempoTranscurrido))
    time.strftime("%H:%M:%S", time.gmtime(tiempoTranscurrido))
    logging.info('Fichero creado correctamente: ' + timenow)
    logging.info('Tiempo de proceso transcurrido: ' + totaltime)
    logging.shutdown()
