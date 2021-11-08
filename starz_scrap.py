import requests
import json

def writeData (archivo, _json):
    editor = open(archivo, 'w')
    to_json = json.dumps(_json, indent=4)
    editor.write(to_json)
    editor.close()

def sliceDate(date):
    slicer = slice(10)
    return date[slicer]

def createLink(type, code):
    link = 'https://www.starz.com/ar/es/' + type + '/' + str(code)
    return link

def createYear(min_year, max_year):
    year = min_year if min_year == max_year else min_year + ' — ' + max_year
    return year

def createGenre(genres):
    clean_genre = ''
    for genre in genres:
        clean_genre = clean_genre + genre['description'] if clean_genre == '' else clean_genre + ', ' + genre['description']
    return clean_genre

def createCredits(credits):
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

def createRuntime(runtime):
    clean_runtime = str(runtime // 60) + ' min'
    return clean_runtime

def createContingency(key, startdate, runtime):
    value = ''
    if key == 'proximamente':
        value = sliceDate(startdate)
    else:
        value = createRuntime(runtime)
    return value

# rq_pagina = Trae todo el contenido de la página
# rq_titulo = Trae todo el contenido de cada título
# rq_temporadas = Trae todas las temporadas de cada título
# rq_episodios = Trae todos los episodios de cada temporada del título

if __name__ == '__main__':
    series = dict()
    peliculas = dict()

    rq_pagina = requests.get('https://playdata.starz.com/metadata-service/play/partner/Web_AR/v8/blocks?playContents=map&lang=es' \
                            '-419&pages=BROWSE,HOME,MOVIES,PLAYLIST,SEARCH,SEARCH%20RESULTS,SERIES&includes=contentId,contentType,' \
                            'title,product,seriesName,seasonNumber,free,comingSoon,newContent,topContentId,properCaseTitle,' \
                            'categoryKeys,runtime,popularity,original,firstEpisodeRuntime,releaseYear,minReleaseYear,maxReleaseYear,' \
                            'episodeCount,detail').json()

    for id in rq_pagina['blocks'][7]['playContentsById']:
        rq_titulo = requests.get('https://playdata.starz.com/metadata-service/play/partner/Web_AR/v8/content?lang=es-419&' \
                                'contentIds=' + id + '&includes=title,logLine,episodeCount,seasonNumber,contentId,releaseYear' \
                                ',minReleaseYear,maxReleaseYear,runtime,genres,ratingCode,studio,contentType,product,comingSoon' \
                                ',startDate,original,childContent,bonusMaterials,previews,free,topContentId,credits,order').json()
        rq_titulo = rq_titulo['playContentArray']['playContents'][0]

        if rq_titulo['contentType'] == 'Series with Season':

            rq_temporadas = rq_titulo['childContent']

            temporadas = dict()
            for t, temporada in enumerate(rq_temporadas):
                
                rq_episodios = temporada['childContent']        
                
                episodios = dict()
                for e, episodio in enumerate(rq_episodios):

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
                
            writeData('starz_series.json', series)
            
        elif rq_titulo['contentType'] == 'Movie':

            released = 'proximamente' if rq_titulo['comingSoon'] else 'duracion'

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
            
            writeData('starz_peliculas.json', peliculas)

#   Código generado con Insomnia
    url = 'https://auth.starz.com/api/v4/Subscriptions/Recurly'

    querystring = {'country':'ar'}

    payload = ''
    headers = {     # Es probable que las credenciales o cookies se desactualicen
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
    rq_pagina = rq_pagina['orderedBuyFlowProducts'][0]['properties']

    modelo_negocio = dict()
    modelo_negocio[rq_pagina['description']] = {
        'duracion' : rq_pagina['PlanIntervalLength'] + ' ' + rq_pagina['PlanIntervalUnit'],
        'precio' : str(int(rq_pagina['AmountInCents']) // 100) + ' ' + rq_pagina['Currency'],
        'prueba_gratis' : rq_pagina['TrialIntervalLength'] + ' ' + rq_pagina['TrialIntervalUnit']
    }

    writeData('starz_modelo.json', modelo_negocio)