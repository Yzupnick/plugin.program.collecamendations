import xbmc
import xbmcplugin
import urllib
import sys
import buggalo

buggalo.GMAIL_RECIPIENT = "chazup@gmail.com"

try:
    from lib.collecamendations import *
    try:
        import StorageServer
    except:
        import lib.storageserverdummy as StorageServer
    cache = StorageServer.StorageServer("collecamendations", 8) # (Your plugin name, Cache time in hours

    def getParameters():
            param=[]
            try:
              paramstring=sys.argv[2]
              if len(paramstring)>=2:
                      params=sys.argv[2]
                      cleanedparams=params.replace('?','')
                      if (params[len(params)-1]=='/'):
                              params=params[0:len(params)-2]
                      pairsofparams=cleanedparams.split('&')
                      param={}
                      for i in range(len(pairsofparams)):
                              splitparams={}
                              splitparams=pairsofparams[i].split('=')
                              if (len(splitparams))==2:
                                      param[splitparams[0]]=splitparams[1]
              return param
            except:
              return param
              
    base_image_url = get_tmdb_configuration() + "original"
    imdb_ids = get_xbmc_movies()
    collections = cache.cacheFunction(organize_movies_by_collections,imdb_ids)

    # Initialize URL parameters
    id = None
    name = None
    menu_number = None          
    params = getParameters()

    # Parse internal URL
    try:
            id = urllib.unquote_plus(params["id"])
    except:
            pass
    try:
            name = urllib.unquote_plus(params["name"])
    except:
            pass
    try:
            menu_number = int(params["mode"])
    except:
            pass

    # Open directories based on selection
    if menu_number == None:
        display_collection_menu(collections)
           
    elif menu_number == 1:
        display_missing_movies(collections[id])
    elif menu_number == 2:
        trailer = get_trailer_from_tmdb(id)
        url = "plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=%s" % trailer
        xbmc.Player(xbmc.PLAYER_CORE_MPLAYER).play(url)

    xbmcplugin.endOfDirectory(int(sys.argv[1]))        
except:
    buggalo.onExceptionRaised()


