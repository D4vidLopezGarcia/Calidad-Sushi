def llamada_sushi():

    import os
    import fitz  # PyMuPDF
    import io
    from PIL import Image
    import tabula
    import pandas as pd
    import numpy as np
    import shutil
    import time
    import re
    import logging
    import configparser
    import sys
    from time import strftime
    import logging.handlers
    import logging.config
    
    
    # Lee archivo configSushi.ini
    config_obj = configparser.ConfigParser()
    config_file = os.path.join(os.path.dirname(__file__), 'configSushiServ.ini')
    config_obj.read(config_file)
    param = config_obj["host"]
    useInfo = config_obj["user_info"]
    rutas = config_obj["rutas"]
    log = config_obj["logData"]
    
    user = param["user"]
    password = param["password"]
    rutaEntrada = rutas["rutaEntrada"]
    rutaSalida = rutas["rutaSalida"]
    rutaArchivoSushi = rutas["rutaArchivoSushi"]
    rutaSalidaImagenes = rutas["rutaSalidaImagenes"]
    rutaSushi = rutas["rutaSushi"]
    regtiendas = rutas["regtiendas"]
    log = log["logData"]
    
    #  Carga de dataframes y diccionarios
    dfTienda = pd.read_excel(regtiendas)
    zip(dfTienda.Centro, dfTienda.Denominacion)
    CentroDenominacion = dict(zip(dfTienda.Centro.astype(str), dfTienda.Denominacion))
    zip(dfTienda.Centro, dfTienda.Poblacion)
    CentroPoblacion = dict(zip(dfTienda.Centro.astype(str), dfTienda.Poblacion))
    zip(dfTienda.Centro, dfTienda.Provincia)
    CentroProvincia = dict(zip(dfTienda.Centro.astype(str), dfTienda.Provincia))
    zip(dfTienda.Centro, dfTienda.Direccion)
    CentroDireccion = dict(zip(dfTienda.Centro.astype(str), dfTienda.Direccion))
    zip(dfTienda.Centro, dfTienda.Telefono)
    CentroTelefono = dict(zip(dfTienda.Centro.astype(str), dfTienda.Telefono))
    
    
    #  diccionario de código de planta
    plantaCode = {'MADRID': 'MAD',
                  'BARCELONA': 'BCN',
                  'VALENCIA': 'VLC',
                  'ALICANTE': 'ALC',
                  'LISBOA': 'LIS'}
    
    # diccionario de código de producto y denominación
    codDenom = {'83300': 'KIT WASABI 10UND',
                '83301': 'KIT SOJA 8UND',
                '83302': 'CALIFORNIA ROLLS (6) CRUNCH',
                '83304': 'SURTIDO 16PZAS S/COMP',
                '83310': 'CALIFORNIA ROLLS (6) COMBINADOS CON PC',
                '83311': 'CALIFORNIA ROLLS (6) COMBINADOS SIN PC',
                '83313': 'MAKIS (8) COMBINADOS CON PC',
                '83314': 'MAKIS (8) COMBINADOS SIN PC',
                '83316': 'NIGIRI (4) ATÚN',
                '83317': 'NIGIRI (4) SALMON',
                '83319': 'NIGIRI (6) MIX',
                '83320': 'SURTIDO 48 PZ',
                '83325': 'ENSALADA ALGA WAKAME',
                '83326': 'GYOZAS LANGOSTINO DESCONGELADAS',
                '83327': 'KIT SUSHI 20 UND',
                '83328': 'JENGIBRE MARINADO TARRINA 30G',
                '83330': 'MIX (8) MAKIS SALMON-ATUN',
                '83333': 'NIGIRI (4) LANGOSTINO',
                '83356': 'TARTAR ATUN 160G',
                '83357': 'SUSHI BOWL 170G',
                '83358': 'ENSALADA ALGA WAKAME CON SALMÓN 160G',
                '83359': 'BENTO BOX 300G',
                '83366': 'BANDEJA SURTIDA SALMON 16 PZAS',
                '83367': 'MAKIS (8) SURTIDO VEGANO',
                '83368': 'SASHIMIS (9) ATUN',
                '83374': 'MAKI (8) SALMON',
                '83375': 'CALIFORNIA ROLLS (6) SALMON/QUESO/S.BLANCO',
                '83396': 'SURTIDO CALIFORNIA ROLLS 16 PZAS',
                '83398': 'SASHIMIS (8) SALMON',
                '83403': 'TARTAR SALMON 160G',
                '83434': 'SUSHI BOWL N 200G',
                '80496': 'SURTIDO ESPECIAL NAVIDAD',
                '85110': 'TEMAKI SALMON',
                '85111': 'TEMAKI ATUN',
                '86006': 'KIT SOJA S/G 8UND'}
    
    
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
            print("El archivo " + file + " NO existe en la ruta indica")
            return False
    
    
    def numeroexpediente(listaarchivos):
        """Sencilla función que extrae el número de expediente del nombre del archivo
           Devuelve los datos en forma de lista
        """
        expedientes = []
        for i in listaarchivos:
            expedientes.append(i[-17:-10])
        return expedientes
    
    
    def tomaprovincia(listaarchivos):
        """Función que extrae la provincia del nombre del archivo
           Devuelve los datos en forma de lista
        """
        provincias = []
        for i in listaarchivos:
            provcat = i[:-27]
            provcatsplit = provcat.split(" ", 4)
            provinc = provcatsplit[0]
            provincias.append(provinc)
        return provincias
    
    
    def tomacategoria(listaarchivos):
        """Función que extrae la categoría del nombre del archivo
           Devuelve los datos en forma de lista
        """
        categorias = []
        for i in listaarchivos:
            provcat = i[:-27]
            provcatsplit = provcat.split(" ", 4)
            categ = provcatsplit[1:]
            categor = " ".join(categ)
            categorias.append(categor)  # CATEGORÍA
        return categorias
    
    
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
        fech = pdf[1]["data"][1][2]["text"][0:10]
        fecha.append(fech)  # FECHA
        # CODIGO TIENDA
        # DIRECCION
        # TELEFONO
        cod = pdf[1]["data"][7][1]["text"]  # CODIGO
        codigo.append(cod)
        # DENOMINACION
        lot = pdf[1]["data"][10][1]["text"]  # LOTE
        lote.append(lot)
        # CATEGORÍA
        # PLANTA
        desc = pdf[1]["data"][19][0]["text"]  # CAUSE
        descripcion.append(desc)
        ud = pdf[1]["data"][14][3]["text"]  # UNITS CLAIMED
        if ud == 'kg':
            ud = 1
            unid = ud
            bandejas.append(unid)
        elif ud == '':
            ud = 0
            unid = ud
            bandejas.append(unid)
        elif ud =='ud':
            ud = 1
            unid = ud
            bandejas.append(unid)
        else:
            unid = re.findall(r'\d+', ud)[0]
            bandejas.append(unid)
        # EXPEDIENTE
        # RESPONSABILIDAD PROVEEDOR VACÍO
        # AC DATAFRAME VACÍO
        # FECHA REVISIÓN
        # FECHA RESPONSABLE
        shutil.move(rutaespanol, destinoarchivo + archivoespanol)
    
    
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
        try:
            if pdf[1]["data"][1][1]["text"] == '':  # FECHA
                fech = pdf[1]["data"][1][4]["text"][0:10]
                fecha.append(fech)
            elif pdf[1]["data"][1][4]["text"] == '':  # FECHA
                fech = pdf[1]["data"][1][1]["text"][0:10]
                fecha.append(fech)
        except:
            fech = 'Rellenad datos manualmente'
            fecha.append(fech)
        #  CÓDIGO TIENDA
        # DIRECCION
        # TELEFONO
        if pdf[1]["data"][5][1]["text"] == '':
            cod = pdf[1]["data"][5][2]["text"]
            codigo.append(cod)
        elif pdf[1]["data"][5][2]["text"] == '':
            cod = pdf[1]["data"][5][1]["text"]
            codigo.append(cod)
        else:
            cod = 'Rellenad datos manualmente'
            codigo.append(cod)
        # DENOMINACION
        if pdf[1]["data"][8][2]["text"] == '':
            lot = pdf[1]["data"][8][1]["text"]  # LOTE
            lote.append(lot)
        elif pdf[1]["data"][8][1]["text"] == '':
            lot = pdf[1]["data"][8][2]["text"]
            lote.append(lot)
        else:
            lot = 'Rellenad datos manualmente'
            lote.append(lot)
        # CATEGORÍA
        # PLANTA
        if pdf[1]["data"][16][1]["text"] == '':
            desc = pdf[1]["data"][16][2]["text"]  # LOTE
            descripcion.append(desc)
        elif pdf[1]["data"][16][2]["text"] == '':
            desc = pdf[1]["data"][16][1]["text"]
            descripcion.append(desc)
        else:
            desc = 'Rellenad datos manualmente'
            descripcion.append(desc)
        if pdf[1]["data"][12][3]["text"] == 'UNIDADES':
            ud = pdf[1]["data"][12][5]["text"]  # UNITS CLAIMED
            if ud == 'kg':
                ud = 1
                unid = ud
                bandejas.append(unid)
            elif ud == '':
                ud = 0
                unid = ud
                bandejas.append(unid)
            elif ud == 'ud':
                ud = 1
                unid = ud
                bandejas.append(unid)
            else:
                unid = re.findall(r'\d+', ud)[0]
                bandejas.append(unid)
        else:
            unid = 'Rellenad datos manualmente'
            bandejas.append(unid)
        # EXPEDIENTE
        # RESPONSABILIDAD PROVEEDOR VACÍO
        # AC DATAFRAME VACÍO
        # FECHA REVISIÓN
        # FECHA RESPONSABLE
        shutil.move(rutaportugues, destinoarchivo + archivoportugues)
    
    
    def creadataframe(dfprovincia):
        """Función que recopila toda la información procesada en las funciones que extraen los PDFs, " \
           genera un dataframe y lo exporta a la ruta establecida
        """
        dfsushi['Fecha'] = fecha
        dfsushi['Código Tienda'] = code
        dfsushi['Tienda'] = dfsushi['Código Tienda'].astype(str).map(CentroDenominacion)
        dfsushi['Provincia'] = dfsushi['Código Tienda'].astype(str).map(CentroProvincia)
        dfsushi['Dirección'] = dfsushi['Código Tienda'].astype(str).map(CentroDireccion)
        dfsushi['Teléfono'] = dfsushi['Código Tienda'].astype(str).map(CentroTelefono)
        dfsushi['Código'] = codigo
        dfsushi['Denominación'] = dfsushi['Código'].astype(str).map(codDenom)
        dfsushi['Lote'] = lote
        dfsushi['Categoría'] = categoria
        dfsushi['Planta'] = dfprovincia['Provincia'].astype(str).map(plantaCode)
        dfsushi['Descripción'] = descripcion
        dfsushi['N. Bandejas'] = bandejas
        dfsushi['Expediente'] = expediente
        dfsushi['Responsabilidad Proveedor'] = pd.DataFrame(columns=['Responsabilidad Proveedor'])  # Crea columna
        # Responsabilidad Proveedor
        dfsushi['Responsabilidad Proveedor'] = dfsushi['Responsabilidad Proveedor'].replace(np.nan, '', regex=True)
        # Elimina los NaN de la columna
        dfsushi['AC'] = pd.DataFrame(columns=['AC'])  # Crea columna AC
        dfsushi['AC'] = dfsushi['AC'].replace(np.nan, '', regex=True)  # Elimina los NaN de la columna
        dfsushi['Fecha Revisión'] = pd.DataFrame(columns=['Fecha Revisión'])  # Crea columna Fecha Revisión
        dfsushi['Fecha Revisión'] = dfsushi['Fecha Revisión'].replace(np.nan, '', regex=True)  # Elimina los NaN de la
        # columna
        dfsushi['Firma Responsable'] = pd.DataFrame(columns=['Firma Responsable'])  # Crea columna Firma Responsable
        dfsushi['Firma Responsable'] = dfsushi['Firma Responsable'].replace(np.nan, '', regex=True)  # Elimina los NaN de
        # la columna
        dfsushi.to_excel(rutaSalida + " " + filexlsx, index=False)  # False elimina el índice en el export
    
    
    start_time = time.time()
    timenow = time.strftime("%d-%b-%Y  %H_%M_%S")
    
    listArchNo = [f for f in sorted(os.listdir(rutaEntrada)) if (str(f))[-3:] == "pdf" and existeono(rutaArchivoSushi,
                                                                                                     f) is False]
    
    listArchNo_with_path = [str(rutaEntrada) + str(f) for f in listArchNo]
    
    #  Comprobación de archivos a cargar. Si no hay archivos, termina la ejecución
    if len(listArchNo) == 0:
        sys.exit('No hay datos a procesar')
    
    #  Descarga de imágenes
    fot = []
    im = 0
    for path in listArchNo:
        # abre el archivo
        rutafull = rutaEntrada + listArchNo[im]
        im = im + 1
        pdf_file = fitz.open(rutafull)
        # itera sobre las páginas del PDF
        for page_index in range(len(pdf_file)):
            # Toma la página misma
            page = pdf_file[page_index]
            image_list = page.getImageList()
            # imprime el número de imágenes encontradas en la página
            if image_list:
                fot.append("SI")
                print(f"[+] Encontradas un total de {len(image_list)} imágenes en la página {page_index}")
            else:
                fot.append("NO")
                print("[!] No se encontraron imágenes en la página", page_index)
            for image_index, img in enumerate(page.getImageList(), start=1):
                # get the XREF of the image
                xref = img[0]
                # extrae los bytes de la imagen
                base_image = pdf_file.extractImage(xref)
                image_bytes = base_image["image"]
                # toma la extensión de la imagen
                image_ext = base_image["ext"]
                # carga la imagen en PIL
                image = Image.open(io.BytesIO(image_bytes))
                # guardamos en disco local
                image.save(open(rutaSalidaImagenes + listArchNo[im - 1][:-4] + f"{page_index}_{image_index}.{image_ext}",
                                "wb"))
        pdf_file.close()
    
    
    oldlogs()
    
    logcreate()
    
    logging.info('Inicio de la ejecución')
    cuentapdfs = len(listArchNo)
    logging.info('Procesando' + ' ' + str(cuentapdfs) + ' ' + 'archivos')
    listArchNo = [f for f in sorted(os.listdir(rutaEntrada)) if (str(f))[-3:] == "pdf" and existeono(rutaArchivoSushi,
                                                                                                     f) is False]
    
    
    filexlsx = 'Input Sushi' + " " + timenow + '.xlsx'
    
    fecha, tienda, direccion, codigo, telefono, denominacion, lote, planta = ([] for i in range(8))
    descripcion, bandejas, respProveedor, ac, fechRevision, firmResponsable = ([] for j in range(6))
    columnas = ['Fecha', 'Código Tienda', 'Tienda', 'Provincia', 'Dirección', 'Teléfono', 'Código', 'Denominación', 'Lote',
                'Categoría', 'Planta', 'Descripción', 'N. Bandejas', 'Expediente', 'Responsabilidad Proveedor', 'AC']
    
    dfsushi = pd.DataFrame(columns=columnas)
    
    expediente = numeroexpediente(listArchNo)
    code = numerocode(listArchNo_with_path)
    provincia = tomaprovincia(listArchNo)
    categoria = tomacategoria(listArchNo)
    
    dfprovincia = pd.DataFrame(columns=['Provincia'])
    dfprovincia['Provincia'] = provincia
    
    for i in range(len(listArchNo)):
        if code[i] > '7000' or code[i] == '7000':
            tienpor(listArchNo_with_path[i], listArchNo[i], rutaArchivoSushi)
        else:
            tienesp(listArchNo_with_path[i], listArchNo[i], rutaArchivoSushi)
    
    creadataframe(dfprovincia)
    
    tiempoTranscurrido = time.time() - start_time
    totaltime = time.strftime("%H:%M:%S", time.gmtime(tiempoTranscurrido))
    time.strftime("%H:%M:%S", time.gmtime(tiempoTranscurrido))
    logging.info('Fichero creado correctamente: ' + timenow)
    logging.info('Tiempo de proceso transcurrido: ' + totaltime)
    logging.shutdown()
