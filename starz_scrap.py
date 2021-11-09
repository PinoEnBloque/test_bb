import requests
import json

def writeData (nombre_archivo: 'str', dict_preparado: 'dict') -> None:
    """
    Función encargada de escribir el diccionario recibido en un archivo json formateado.

    nombre_archivo = Nombre que tendrá el archivo .json.
    dict_preparado = Diccionario ya armado para ser convertido a json.
    
    """
    editor = open(nombre_archivo, 'w')
    to_json = json.dumps(dict_preparado, indent=4)
    editor.write(to_json)
    editor.close()

def sliceDate(date: 'str') -> str:
    """
    Función encargada de recibir una fecha en un formato extendido, abreviarlo a sólo fecha y devolverlo.

    """
    slicer = slice(10)
    return date[slicer]

def createLink(tipo_contenido: 'str', id_contenido: 'str') -> str:
    """
    Función que recibe los indicadores del hipervínculo y los devuelve en una URL válida.

    'tipo_contenido' debe ser movie/series/artist para que la URL funcione.

    """
    link = 'https://www.starz.com/ar/es/' + tipo_contenido + '/' + str(id_contenido)
    return link

def createYear(min_year: 'str', max_year: 'str') -> str:
    """
    Función que determina si el año de publicación es sólo uno o fue publicado entre un intervalo
    de años, y devuelve una cadena de texto acorde.

    """
    year = min_year if min_year == max_year else min_year + ' — ' + max_year
    return year

def createGenre(genres: 'dict') -> str:
    """
    Función que recibe un diccionario de géneros del contenido y los devuelve en un solo string.

    """
    clean_genre = ''
    for genre in genres:
        clean_genre = clean_genre + genre['description'] if clean_genre == '' else clean_genre + ', ' + genre['description']
    return clean_genre

def createCredits(credits: 'list') -> dict:
    """
    Función que recibe la lista de diccionarios del elenco de un contenido, pone todos los roles
    (actor, director, etcétera) en un mismo string, y lo devuelve como diccionario.
    Las key están compuestas por el link.

    """
    elenco = dict() 
    for credit in credits: 
        clean_role = ''
        roles = credit['keyedRoles']  
        for role in roles:
            clean_role = clean_role + role['name'] if clean_role == '' else clean_role + ', ' + role['name']
        elenco[createLink('artist', credit['id'])] = {
            'nombre' : credit['name'],
            'rol' : clean_role
        }
    return elenco

def createRuntime(runtime: 'int') -> str:
    """
    Función que convierte el tiempo de minutos a horas y le agrega el string 'min' al final.

    """
    clean_runtime = str(runtime // 60) + ' min'
    return clean_runtime

def createContingency(key: 'str', startdate: 'str', runtime: 'int') -> str:
    """
    Función que devuelve una value para un diccionario. Evalúa, según la key que recibe la función, si 
    el contenido ya está disponible en la plataforma o no. 
    Si está, devuelve su duración.
    Si no está, devuelve la fecha en que se estrenará.

    """
    value = ''
    if key == 'proximamente':
        value = sliceDate(startdate)
    else:
        value = createRuntime(runtime)
    return value


if __name__ == '__main__':

    # rq_pagina = Trae todo el contenido de la página
    # rq_titulo = Trae todo el contenido de cada título
    # rq_temporadas = Trae todas las temporadas de cada título
    # rq_episodios = Trae todos los episodios de cada temporada del título
 
    series = dict()         # Contendrá un diccionario con todas las series.
    peliculas = dict()      # Contendrá un diccionario con todas las películas.

    rq_pagina = requests.get('https://playdata.starz.com/metadata-service/play/partner/Web_AR/v8/blocks?playContents=map&lang=es' \
                            '-419&pages=BROWSE,HOME,MOVIES,PLAYLIST,SEARCH,SEARCH%20RESULTS,SERIES&includes=contentId,contentType,' \
                            'title,product,seriesName,seasonNumber,free,comingSoon,newContent,topContentId,properCaseTitle,' \
                            'categoryKeys,runtime,popularity,original,firstEpisodeRuntime,releaseYear,minReleaseYear,maxReleaseYear,' \
                            'episodeCount,detail').json()

    for id in rq_pagina['blocks'][7]['playContentsById']:   # Por cada "ContentId" en la página (Es decir, por cada contenido)...
        rq_titulo = requests.get('https://playdata.starz.com/metadata-service/play/partner/Web_AR/v8/content?lang=es-419&' \
                                'contentIds=' + id + '&includes=title,logLine,episodeCount,seasonNumber,contentId,releaseYear' \
                                ',minReleaseYear,maxReleaseYear,runtime,genres,ratingCode,studio,contentType,product,comingSoon' \
                                ',startDate,original,childContent,bonusMaterials,previews,free,topContentId,credits,order').json()
        rq_titulo = rq_titulo['playContentArray']['playContents'][0]    # Guardamos la dirección donde está lo que nos interesa.

        if rq_titulo['contentType'] == 'Series with Season': # Si el contenido es una serie...

            rq_temporadas = rq_titulo['childContent']           # Aquí es donde encontramos todas las temporadas de la serie.

            temporadas = dict()                                 # Contendrá los metadatos ordenados de la temporada.
            for temporada in rq_temporadas:
                
                rq_episodios = temporada['childContent']        # Aquí es donde encontramos todos los episodios de la temporada.
                
                episodios = dict()                              # Contendrá los metadatos ordenados del episodio.
                for episodio in rq_episodios:

                    episodios[createLink('series', episodio['contentId'])] = {    
                        'titulo' : str(episodio['order']) + ' ' + episodio['title'],
                        'año' : episodio['releaseYear'],
                        'duracion' : createRuntime(episodio['runtime']),
                        'sinopsis' : episodio['logLine']
                    }
                    temporadas[createLink('series', temporada['contentId'])] = {
                        'titulo' : temporada['title'],
                        'año' : createYear(temporada['minReleaseYear'], temporada['maxReleaseYear']),
                        'sinopsis' : temporada['logLine'],
                        'episodios' : episodios
                    }

            series[createLink('series', id)] = {
                'titulo' : rq_titulo['title'],
                'año' : createYear(rq_titulo['minReleaseYear'], rq_titulo['maxReleaseYear']),
                'edad' : rq_titulo['ratingCode'], 
                'estudio' : rq_titulo['studio'],
                'genero' : createGenre(rq_titulo['genres']),
                'sinopsis' : rq_titulo['logLine'],
                'elenco' : createCredits(rq_titulo['credits']),
                'temporadas' : temporadas,
                }
                
            writeData('starz_series.json', series)  # Escribimos en el json de las series por cada iteración. (Podría cambiar)
            
        elif rq_titulo['contentType'] == 'Movie': # Si el contenido es una película...

            released = 'proximamente' if rq_titulo['comingSoon'] else 'duracion'    # Comprobamos si el contenido está disponible o no.

            peliculas[createLink('movies', id)] = {
                'titulo' : rq_titulo['title'],
                'año' : rq_titulo['releaseYear'],
                'edad' : rq_titulo['ratingCode'], 
                'estudio' : rq_titulo['studio'],
                'generos' : createGenre(rq_titulo['genres']),
                released : createContingency(released, rq_titulo.get('startDate'), rq_titulo.get('runtime')),
                'sinopsis' : rq_titulo['logLine'],
                'elenco' : createCredits(rq_titulo['credits'])
                }   
            
            writeData('starz_peliculas.json', peliculas) # Escribimos en el json de las pelis por cada iteración. (Podría cambiar)

#   Código generado por Insomnia. Lleva los headers necesarios para que la información sea accesible.
    try:
        url = 'https://auth.starz.com/api/v4/Subscriptions/Recurly'

        querystring = {'country':'ar'}

        payload = ''
        headers = {                                                         # Es probable que las credenciales se desactualicen...
            'authority': 'auth.starz.com',
            'accept': 'application/json, text/plain, */*',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
            'authtokenauthorization': 'PLAYAUTH1.0 x=nonce=wQM8gM4H, apikey=A81FB88033CD4DC4A47801D19288306E,' \
                'signature_method=SHA256, requesttime=2021-11-08T18:06:37.182Z, deviceid=fbde51016aea4741b38e38a' \
                '75a5ad83c, AllowAuthNOnly=true, platformtype=HTML5, platformversion=Chrome, platformostype=Windows' \
                ',platformosversion=10, signature=tRtVKGOWGoDOkOjpv5FeZQKOGWiJMCrNcQbN81jzoCU=',
            'sec-gpc': '1',
            'origin': 'https://www.starz.com',
            'sec-fetch-site': 'same-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://www.starz.com/',
            'accept-language': 'es-ES,es;q=0.9'
        }

        rq_pagina = requests.request('GET', url, data=payload, headers=headers, params=querystring).json()
        rq_pagina = rq_pagina['orderedBuyFlowProducts'][0]['properties']    # Aquí es donde encontramos la información del tipo de negocio.

        modelo_negocio = dict()                                             # Contendrá los metadatos ordenados del tipo de negocio.
        modelo_negocio[rq_pagina['description']] = {
            'duracion' : rq_pagina['PlanIntervalLength'] + ' ' + rq_pagina['PlanIntervalUnit'],
            'precio' : str(int(rq_pagina['AmountInCents']) // 100) + ' ' + rq_pagina['Currency'],
            'prueba_gratis' : rq_pagina['TrialIntervalLength'] + ' ' + rq_pagina['TrialIntervalUnit']
        }

        writeData('starz_modelo.json', modelo_negocio)                      # Escribimos en el json la metadata del tipo de negocio.
        
    except:
        print('No se ha podido obtener el modelo de negocio. ¿Autenticación expirada?')