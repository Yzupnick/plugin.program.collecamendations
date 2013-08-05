import urllib2
import urllib
import json
import xbmcgui
import xbmcplugin
import xbmc
import sys

class Movie(object):
    def __init__(self,title,id,collection_id,poster_path,,imdb_id,own = False):
        self.title = title
        self.id = id
        self.own = own
        self.collection_id = collection_id
        self.poster_path = poster_path
        self.imdb_id = imdb_id

class Collection(object):
    def __init__(self,name,id,poster_path,own_all = False):
        self.name = name
        self.id = id
        self.own_all = own_all
        self.movies = []
        self.poster_path = poster_path

def get_tmdb_configuration():
    request = urllib2.Request("http://api.themoviedb.org/3/configuration?api_key=%s" % API_KEY, headers={"Accept" : "application/json"})
    response = urllib2.urlopen(request).read()
    data = json.loads(response)
    return data['images']['base_url']
    
def get_trailer_from_tmdb(tmdb_id):
    request = urllib2.Request("http://api.themoviedb.org/3/movie/%s/trailers?api_key=%s" % (tmdb_id,API_KEY), headers={"Accept" : "application/json"})
    response = urllib2.urlopen(request).read()
    data = json.loads(response)
    return data['youtube'][0]["source"]

def get_movie_by_id(id):
    request = urllib2.Request("http://api.themoviedb.org/3/movie/%s?api_key=%s" % (id,API_KEY), headers={"Accept" : "application/json"})
    response = urllib2.urlopen(request).read()
    data = json.loads(response)
    collection = str(data["belongs_to_collection"]['id']) if data["belongs_to_collection"]  is not None else None
    movie = Movie(title=data['title'], id=str(data['id']),collection_id=collection,poster_path=base_image_url + data["poster_path"],imdb_id=data["imdb_id"])
    return movie

def get_collection(collection_id):
    request = urllib2.Request("http://api.themoviedb.org/3/collection/%s?api_key=%s" % (collection_id,API_KEY), headers={"Accept" : "application/json"})
    response = urllib2.urlopen(request).read()
    data = json.loads(response)
    collection = Collection(name=data["name"],id=str(data["id"]),poster_path=base_image_url + data["poster_path"])
    for part in data["parts"]:
        movie = Movie(title=part['title'], id=str(part['id']),own=False,collection_id=collection.id,poster_path= base_image_url + part["poster_path"])
        collection.movies.append(movie)
    return collection

def organize_movies_by_collections(imdb_ids):
    collections ={}
    for imdb_id in imdb_ids:
        current_movie = get_movie_by_id(imdb_id)
        
        if current_movie.collection_id is not None:  
            if current_movie.collection_id in collections:
                current_collection = collections[current_movie.collection_id]
            else:
                current_collection = get_collection(current_movie.collection_id)
                collections[current_movie.collection_id] = current_collection

            movies_in_collection_owned = 0    
            for movie in current_collection.movies:
                if movie.id == current_movie.id:
                    movie.own = True
                    movies_in_collection_owned += 1

            if len(current_collection.movies) == movies_in_collection_owned:
                current_collection.own_all = True
    return collections

                
def addCollectionDirectory(collection_name, collection_id, menu_number, thumbnail_path, movie_total):
    return_url = sys.argv[0]+"?id="+urllib.quote_plus(str(collection_id))+"&mode="+str(menu_number)+"&name="+urllib.quote_plus(collection_name.encode( "utf-8" ))
    list_item = xbmcgui.ListItem(collection_name, thumbnailImage=thumbnail_path)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=return_url, listitem=list_item, isFolder=True, totalItems=movie_total)
    
def addMovieDirectory(movie_name, movie_id, menu_number, thumbnail_path,imdb_id):
    return_url = sys.argv[0]+"?id="+urllib.quote_plus(str(movie_id))+"&mode="+str(menu_number)+"&name="+urllib.quote_plus(movie_name.encode( "utf-8" ))
    list_item = xbmcgui.ListItem(movie_name, thumbnailImage=thumbnail_path)
    CP_ADD_VIA_IMDB = 'XBMC.RunPlugin(plugin://plugin.video.couchpotato_manager/movies/add?imdb_id=%s)'
    TRAKT_ADD_URL = 'XBMC.RunPlugin(plugin://plugin.video.trakt_list_manager/movies/add?imdb_id=%s)'
    list_item.addContextMenuItems([('Add Movie to CouchPotato', CP_ADD_VIA_IMDB % imdb_id)])
    list_item.addContextMenuItems([('Add Movie on Trakt.tv', TRAKT_ADD_URL % imdb_id)])
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=return_url, listitem=list_item, isFolder=False) 


def get_xbmc_movies():
    query = {
        'jsonrpc': '2.0',
        'id': 0,
        'method': 'VideoLibrary.GetMovies',
        'params': {
            'properties': ['imdbnumber']
        }
    }
    response = json.loads(xbmc.executeJSONRPC(json.dumps(query)))
    imdb_ids = [movie['imdbnumber'] for movie in response['result']['movies']]
    return imdb_ids

def display_collection_menu(collections):
    for key in collections:
        collection = collections[key]
        if not collection.own_all:
            addCollectionDirectory(collection.name,collection.id,1,collection.poster_path,len(collection.movies))
  
def display_missing_movies(collection):
    for movie in collection.movies:
        if not movie.own:
            addMovieDirectory(movie.title, movie.id, 2, movie.poster_path,movie.imdb_id)

API_KEY = "aba0b2149e9390bccb85fa864dd60343"
base_image_url = get_tmdb_configuration() + "original"
