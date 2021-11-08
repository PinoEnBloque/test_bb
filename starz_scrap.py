import requests
import json

def writeData (archivo, _json):
    editor = open(archivo, "w")
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
    year = min_year if min_year == max_year else min_year + " — " + max_year
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

series = dict()
peliculas = dict()

# rq_pagina = Trae todo el contenido de la página
# rq_titulo = Trae todo el contenido de cada título
# rq_temporadas = Trae todas las temporadas de cada título
# rq_episodios = Trae todos los episodios de cada temporada del título

rq_pagina = requests.get('https://playdata.starz.com/metadata-service/play/partner/Web_AR/v8/blocks?playContents=map&lang=es-419&pages=BROWSE,HOME,MOVIES,PLAYLIST,SEARCH,SEARCH%20RESULTS,SERIES&includes=contentId,contentType,title,product,seriesName,seasonNumber,free,comingSoon,newContent,topContentId,properCaseTitle,categoryKeys,runtime,popularity,original,firstEpisodeRuntime,releaseYear,minReleaseYear,maxReleaseYear,episodeCount,detail').json()

for id in rq_pagina['blocks'][7]['playContentsById']:
    rq_titulo = requests.get('https://playdata.starz.com/metadata-service/play/partner/Web_AR/v8/content?lang=es-419&contentIds=' + id + '&includes=title,logLine,episodeCount,seasonNumber,contentId,releaseYear,minReleaseYear,maxReleaseYear,runtime,genres,ratingCode,studio,contentType,product,comingSoon,startDate,original,childContent,bonusMaterials,previews,free,topContentId,credits,order').json()
    rq_titulo = rq_titulo['playContentArray']['playContents'][0]

    if rq_titulo['contentType'] == 'Series with Season':
        link = createLink('series', id)
        genre = createGenre(rq_titulo['genres'])
        credit = createCredits(rq_titulo['credits'])

        rq_temporadas = rq_titulo['childContent']

        temporadas = dict()
        for t, temporada in enumerate(rq_temporadas):
            
            rq_episodios = temporada['childContent']        
            
            episodios = dict()
            for e, episodio in enumerate(rq_episodios):

                episodios[createLink('series', episodio['contentId'])] = {    
                    'titulo' : str(episodio['order']) + ' ' + episodio['title'],
                    'año' : episodio['releaseYear'],
                    'sinopsis' : episodio['logLine']
                }
                temporadas[createLink('series', temporada['contentId'])] = {
                    'titulo' : temporada['title'],
                    'año' : createYear(temporada['minReleaseYear'], temporada['maxReleaseYear']),
                    'sinopsis' : temporada['logLine'],
                    'episodios' : episodios
                }

        series[link] = {
            'titulo' : rq_titulo['title'],
            'año' : createYear(rq_titulo['minReleaseYear'], rq_titulo['maxReleaseYear']),
            'edad' : rq_titulo['ratingCode'], 
            'estudio' : rq_titulo['studio'],
            'genero' : genre,
            'sinopsis' : rq_titulo['logLine'],
            'elenco' : createCredits(rq_titulo['credits']),
            'temporadas' : temporadas,
            }
            
        writeData("starz_series.json", series)
        
    elif rq_titulo['contentType'] == 'Movie':
        link = createLink('movies', id)
        genre = createGenre(rq_titulo['genres'])

        peliculas[link] = {
            'titulo' : rq_titulo['title'],
            'año' : rq_titulo['releaseYear'],
            'edad' : rq_titulo['ratingCode'], 
            'estudio' : rq_titulo['studio'],
            'generos' : genre,
            'sinopsis' : rq_titulo['logLine'],
            }   
        if rq_titulo['comingSoon']: 
            peliculas[link]['proximamente'] = sliceDate(rq_titulo['startDate'])
        else:
            peliculas[link]['duracion'] = str(rq_titulo['runtime'] // 60) + " min"
        peliculas[link]['elenco'] = createCredits(rq_titulo['credits'])

        writeData("starz_peliculas.json", peliculas)