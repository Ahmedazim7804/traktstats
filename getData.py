from cProfile import run
import os
import sys
import json
import time
import pickle
import requests
from tqdm import tqdm
from merry import Merry
from copy import deepcopy
from dotmap import DotMap
from rapidfuzz import fuzz
from operator import itemgetter
from tmdbv3api import TV
from tmdbv3api import TMDb
from tmdbv3api import Movie
from tmdbv3api import Season
from tmdbv3api import Episode
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtWebEngineWidgets import QWebEngineView
from joblib import Parallel, delayed


# Uncomment Bottom line if you want to download the data again
# FirstRun = True


tmdb = TMDb()
tmdb.api_key = tmdb_API_KEY = os.environ['TMDB_API_KEY']
trakt_CLIENT_ID = os.environ['TRAKT_API_KEY']


merry = Merry()

@merry._except
def update_files_on_error():
    update_files()
    sys.exit()

@merry._try
def get_genres(tmdb_id, type_of_item):
    if tmdb_id not in info.keys():
        info[tmdb_id] = {}

    if 'genres' in info.get(tmdb_id, {}).keys() and not firstRun:
        genres = info[tmdb_id]['genres']
    else:
        genres = []
        if type_of_item == 'movie':
            item_info = TMDbMovie.details(tmdb_id)['genres']
        else:
            item_info = TMDbTV.details(tmdb_id)['genres']

        for genre in item_info:
            genre = genre['name']
            if ' & ' in genre:
                genres.extend(genre.split(' & '))
            else:
                genres.append(genre)

        info[tmdb_id]['genres'] = genres

    return genres

@merry._try
def get_runtime(tmdb_id, type_of_item, tmdb_show_id=0, trakt_show_id=0, season=0, episode=0):
    if tmdb_id not in info.keys():
        info[tmdb_id] = {}

    if 'runtime' in info.get(tmdb_id, {}).keys() and not firstRun:
        runtime = info[tmdb_id]['runtime']
    else:
        if type_of_item == 'movie':
            runtime = TMDbMovie.details(tmdb_id)['runtime']
        else:
            runtime = TMDbEpisode.details(tmdb_show_id, season, episode)['runtime']
            if not runtime:
                url = f"https://api.trakt.tv/shows/{trakt_show_id}/seasons/{season}/episodes/{episode}?extended=full"
                runtime = requests.get(url, headers=headers).json()['runtime']
        info[tmdb_id]['runtime'] = runtime

    return runtime

@merry._try
def get_network(tmdb_id, trakt_id):
    if tmdb_id not in info.keys():
        info[tmdb_id] = {}

    if 'network' in info.get(tmdb_id, {}).keys() and not firstRun:
        id = info[tmdb_id]['network']
    else:
        baseurl = "https://api.trakt.tv/shows/{}?extended=full"
        url = baseurl.format(trakt_id)
        network = requests.get(url, headers=headers).json()['network']
        networks_tmdb_data = TMDbTV.details(tmdb_id)['networks']
        networks_tmdb_data = {i['name']: i for i in networks_tmdb_data}

        if network not in networks_tmdb_data.keys():
            for tmdb_network in networks_tmdb_data:
                print('fuzzy matching network')
                if fuzz.ratio(network, tmdb_network) > 90 or fuzz.partial_ratio(network, tmdb_network):
                    network = tmdb_network
                    break
            else:
                print('Randomly Selecting Network')
                network = list(networks_tmdb_data.keys())[0]

        url, id = itemgetter('logo_path', 'id')(networks_tmdb_data[network])
        id = str(id)
        download_tmdb_image(url=url, basepath='network_icons', filename=f"{id}", size='200')

        if id not in networks.keys():
            networks[id] = network

        info[tmdb_id]['network'] = id

    return id

@merry._try
def get_studios(tmdb_id):
    if tmdb_id not in info.keys():
        info[tmdb_id] = {}

    if 'studios' in info.get(tmdb_id, {}).keys() and not firstRun:
        studios = info[tmdb_id]['studios']
    else:
        studios = []
        studios_data = TMDbMovie.details(tmdb_id).production_companies

        for studio in studios_data:
            id, name, url = itemgetter('id', 'name', 'logo_path')(studio)
            id = str(id)

            studio_image_path = download_tmdb_image(url=url, basepath='studios/', filename=f"{id}", size=200)
            if not studio_image_path:
                continue

            studios.append(id)

            studioslst[id] = name

        info[tmdb_id]['studios'] = studios

    return studios

@merry._try
def get_poster(tmdb_id, type_of_item):
    if tmdb_id not in info.keys():
        info[tmdb_id] = {}

    if 'poster' in info.get(tmdb_id, {}).keys() and not firstRun:
        poster = info[tmdb_id]['poster']
    else:
        if type_of_item == 'movie':
            poster = TMDbMovie.details(tmdb_id).poster_path
        else:
            poster = TMDbTV.details(tmdb_id).poster_path

    info[tmdb_id]['poster'] = poster

    return poster

@merry._try
def get_cast(tmdb_id, type_of_item, tmdb_show_id=0, season=0, episode=0):
    if tmdb_id not in info.keys():
        info[tmdb_id] = {}

    if 'cast' in info.get(tmdb_id, {}).keys() and not firstRun:
        item_cast = info[tmdb_id]['cast']
    else:
        item_cast = []
        if type_of_item == 'movie':
            item_cast = TMDbMovie.credits(tmdb_id)['cast']
        if type_of_item == 'tv':
            url = f"https://api.themoviedb.org/3/tv/{tmdb_show_id}/season/{season}/episode/{episode}/credits?api_key={tmdb_API_KEY}&language=en-US"
            item_cast = requests.get(url).json()['cast']
            guest_cast = requests.get(url).json()['guest_stars']
            item_cast.extend(guest_cast)

        for actor in item_cast:
            name, id, gender, image = itemgetter('name', 'id', 'gender', 'profile_path')(actor)
            castlist[id] = {'name': name, 'gender': gender, 'image': image}

        item_cast = [actor['id'] for actor in item_cast]

    info[tmdb_id]['cast'] = item_cast

    return item_cast

@merry._try
def get_crew(tmdb_id, type_of_item, tmdb_show_id=0, season=0, episode=0):
    if tmdb_id not in info.keys():
        info[tmdb_id] = {}

    if 'crew' in info.get(tmdb_id, {}).keys() and not firstRun:
        item_crew = info[tmdb_id]['crew']
    else:
        item_crew = {}
        if type_of_item == 'movie':
            full_crew = TMDbMovie.credits(tmdb_id)['crew']
        else:
            url = f"https://api.themoviedb.org/3/tv/{tmdb_show_id}/season/{season}/episode/{episode}/credits?api_key={tmdb_API_KEY}&language=en-US"
            full_crew = requests.get(url).json()['crew']

        have_writer = False
        for _crew in full_crew:
            job = _crew['job']
            if job == 'Director':
                name, id, image = itemgetter('name', 'id', 'profile_path')(_crew)
                crewlist[id] = {'name': name, 'image': image}
                item_crew[job] = item_crew.get(job, []) + [id]
            elif job == 'Writer':
                have_writer = True
                name, id, image = itemgetter('name', 'id', 'profile_path')(_crew)
                crewlist[id] = {'name': name, 'image': image}
                item_crew[job] = item_crew.get(job, []) + [id]

        if not have_writer:
            for _crew in full_crew:
                job = _crew['job']
                if job == 'Screenplay':
                    job = 'Writer'
                    name, id, image = itemgetter('name', 'id', 'profile_path')(_crew)
                    crewlist[id] = {'name': name, 'image': image}
                    item_crew[job] = item_crew.get(job, []) + [id]

    info[tmdb_id]['crew'] = item_crew

    return item_crew

@merry._try
def get_countries(tmdb_id, trakt_id, type_of_item):
    if tmdb_id not in info.keys():
        info[tmdb_id] = {}

    if 'countries' in info.get(tmdb_id, {}).keys() and not firstRun:
        countries = info[tmdb_id]['countries']
    else:
        if type_of_item == 'tv':
            baseurl = 'https://api.trakt.tv/shows/{}?extended=full'
        else:
            baseurl = 'https://api.trakt.tv/movies/{}?extended=full'
        url = baseurl.format(trakt_id)

        response = requests.get(url, headers=headers).json()
        countries = response["country"]

    info[tmdb_id]['countries'] = countries

    return countries

def run_parallely(fn, items):
    return Parallel(n_jobs=-2, backend='threading', require='sharedmem')(delayed(fn)(item) for item in items)

@merry._try
def parse_movie_data():
    print('Parsing Movies Data')
    run_parallely(process_watched_movies, tqdm(data['history']))

def process_watched_movies(item):
    type = item['type']
    if type == 'movie':
        tmdb_id, trakt_id = itemgetter('tmdb', 'trakt')(item['movie']['ids'])
        if tmdb_id not in watched_movies.keys():
            watched_movies[tmdb_id] = DotMap()
            watched_movies[tmdb_id]['title'] = item['movie']['title']
            watched_movies[tmdb_id]['time'] = [item['watched_at']]
            watched_movies[tmdb_id]['plays'] = 1
            watched_movies[tmdb_id]['released_year'] = item['movie']['year']
            watched_movies[tmdb_id]['id'] = str(tmdb_id)
            watched_movies[tmdb_id]['type'] = type
            watched_movies[tmdb_id]['trakt_id'] = trakt_id
            watched_movies[tmdb_id]['rating'] = ratings[tmdb_id] if tmdb_id in ratings.keys() else 0
            watched_movies[tmdb_id]['runtime'] = get_runtime(tmdb_id, 'movie')
            watched_movies[tmdb_id]['genres'] = get_genres(tmdb_id, 'movie')
            watched_movies[tmdb_id]['poster'] = get_poster(tmdb_id, 'movie')
            watched_movies[tmdb_id]['country'] = get_countries(tmdb_id, trakt_id, 'movie')
            watched_movies[tmdb_id]['studios'] = get_studios(tmdb_id)
            watched_movies[tmdb_id]['cast'] = get_cast(tmdb_id, 'movie')
            watched_movies[tmdb_id]['crew'] = get_crew(tmdb_id, 'movie')
        else:
            watched_movies[tmdb_id]['plays'] += 1
            watched_movies[tmdb_id]['time'].append(item['watched_at'])

@merry._try
def parse_shows_data():
    print('Parsing TV Data')
    run_parallely(process_watched_episodes, tqdm(data['history']))
    run_parallely(process_watched_shows, data['watched'])

def process_watched_episodes(item):
    type = item['type']
    if type == 'episode':
        tmdb_id = item['episode']['ids']['tmdb']
        tmdb_show_id, trakt_show_id = itemgetter('tmdb', 'trakt')(item['show']['ids'])
        if tmdb_id not in watched_episodes.keys():
            watched_episodes[tmdb_id] = DotMap()
            watched_episodes[tmdb_id]['title'] = item['episode']['title']
            watched_episodes[tmdb_id]['season'] = season = item['episode']['season']
            watched_episodes[tmdb_id]['episode'] = episode = item['episode']['number']
            watched_episodes[tmdb_id]['time'] = [item['watched_at']]
            watched_episodes[tmdb_id]['plays'] = 1
            watched_episodes[tmdb_id]['show'] = item['show']['title']
            watched_episodes[tmdb_id]['tmdb_show_id'] = tmdb_show_id
            watched_episodes[tmdb_id]['type'] = type
            watched_episodes[tmdb_id]['rating'] = ratings[tmdb_id] if tmdb_id in ratings.keys() else 0
            watched_episodes[tmdb_id]['runtime'] = get_runtime(tmdb_id, 'tv', tmdb_show_id=tmdb_show_id, trakt_show_id=trakt_show_id, season=season, episode=episode)
            watched_episodes[tmdb_id]['cast'] = get_cast(tmdb_id, 'tv', tmdb_show_id=tmdb_show_id, season=season, episode=episode)
            watched_episodes[tmdb_id]['crew'] = get_crew(tmdb_id, 'tv', tmdb_show_id=tmdb_show_id, season=season, episode=episode)
        else:
            watched_episodes[tmdb_id]['plays'] += 1
            watched_episodes[tmdb_id]['time'].append(item['watched_at'])

def process_watched_shows(item):
    if 'show' in item.keys():
        tmdb_id, trakt_id = itemgetter('tmdb', 'trakt')(item['show']['ids'])

        watched_shows[tmdb_id] = DotMap()
        watched_shows[tmdb_id]['id'] = str(tmdb_id)
        watched_shows[tmdb_id]['title'] = item['show']['title']
        watched_shows[tmdb_id]['plays'] = item['plays']
        watched_shows[tmdb_id]['trakt_id'] = str(trakt_id)
        watched_shows[tmdb_id]['released_year'] = item['show']['year']
        watched_shows[tmdb_id]['rating'] = ratings[tmdb_id] if tmdb_id in ratings.keys() else 0
        watched_shows[tmdb_id]['network'] = get_network(tmdb_id, trakt_id)
        watched_shows[tmdb_id]['genres'] = get_genres(tmdb_id, 'tv')
        watched_shows[tmdb_id]['poster'] = get_poster(tmdb_id, 'tv')
        watched_shows[tmdb_id]['country'] = get_countries(tmdb_id, trakt_id, 'tv')

@merry._try
def download_tmdb_image(url, basepath, filename, size):

    url = f"https://image.tmdb.org/t/p/w{size}/{url}"

    extension = url[-4:]

    path = os.path.join(".cache", basepath, filename+extension)

    if not os.path.exists(path):
        request = requests.get(url)
        if request.status_code != 200:
            return False
        with open(path, 'wb') as icon_file:
            icon_file.write(request.content)
        time.sleep(0.5)

    return path


@merry._try
def get_top_shows_and_movies_lists():

    if list_of_lists:
        return

    imdb_top_250_shows = requests.get("https://api.trakt.tv/lists/imdb-top-rated-tv-shows/items",headers=headers).json()
    trakt_top_250_shows = requests.get("https://api.trakt.tv/lists/trakt-popular-tv-shows/items",headers=headers).json()
    rollingstone_top_100_shows = requests.get("https://api.trakt.tv/lists/rolling-stone-s-100-greatest-tv-shows-of-all-time/items", headers=headers).json()

    imdb_top_250_movies = requests.get("https://api.trakt.tv/lists/imdb-top-rated-movies/items", headers=headers).json()
    trakt_top_250_movies = requests.get("https://api.trakt.tv/lists/trakt-popular-movies/items", headers=headers).json()
    reddit_top_250_movies = requests.get("https://api.trakt.tv/lists/reddit-top-250-2019-edition/items",headers=headers).json()

    most_played_show_trakt = requests.get("https://api.trakt.tv/shows/played/all", headers=headers).json()
    most_played_movies_trakt = requests.get("https://api.trakt.tv/movies/played/all", headers=headers).json()


    imdb_top_250_shows = [i['show']['ids']['tmdb'] for i in imdb_top_250_shows]
    trakt_top_250_shows = [i['show']['ids']['tmdb'] for i in trakt_top_250_shows]
    rollingstone_top_100_shows = [i['show']['ids']['tmdb'] for i in rollingstone_top_100_shows]

    imdb_top_250_movies = [i['movie']['ids']['tmdb'] for i in imdb_top_250_movies]
    trakt_top_250_movies = [i['movie']['ids']['tmdb'] for i in trakt_top_250_movies]
    reddit_top_250_movies = [i['movie']['ids']['tmdb'] for i in reddit_top_250_movies]

    most_played_show_trakt = {show['show']['ids']['tmdb']: show for show in most_played_show_trakt}
    most_played_movies_trakt = {show['movie']['ids']['tmdb']: show for show in most_played_movies_trakt}

    list_of_lists['shows'] = {
        'imdb': imdb_top_250_shows,
        'trakt': trakt_top_250_shows,
        'rollingstone': rollingstone_top_100_shows
    }

    list_of_lists['movies'] = {
        'imdb': imdb_top_250_movies,
        'trakt': trakt_top_250_movies,
        'reddit': reddit_top_250_movies
    }

    list_of_lists['trakt'] = {
        'most_played_shows': most_played_show_trakt,
        'most_played_movies': most_played_movies_trakt
    }


def update_files():
    if info != info_copy:
        print("saving info")
        file = open('info.dict', 'wb')
        pickle.dump(info, file)
        file.close()

    if json_data != json_data_copy:
        print("saving json_data")
        file = open('json_data.json', 'w')
        json.dump(json_data, file)
        file.close()


@merry._try
def getData():
    parse_movie_data()
    parse_shows_data()
    get_top_shows_and_movies_lists()
    update_files()
    return watched_movies, watched_episodes, watched_shows, len(ratings), len(data['lists']), json_data, name, joined_date


headers = {
    'Content-Type': 'application/json',
    'trakt-api-version': '2',
    'trakt-api-key': trakt_CLIENT_ID,
}


tmdb.language = 'en'
TMDbMovie = Movie()
TMDbTV = TV()
TMDbSeason = Season()
TMDbEpisode = Episode()

watched_movies = DotMap()
watched_shows = DotMap()
watched_episodes = DotMap()

if os.path.exists('data.json'):
    filename = "data.json"
else:
    app = QtWidgets.QApplication(sys.argv)

    messagebox = QtWidgets.QMessageBox()
    messagebox.setIcon(QtWidgets.QMessageBox.Information)
    messagebox.setTextFormat(QtCore.Qt.RichText)
    messagebox.setText("Select full exported data file from <a href='https://github.com/seanbreckenridge/traktexport'>traktexport</a>")
    messagebox.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)

    if messagebox.exec_() == QtWidgets.QMessageBox.Cancel:
        sys.exit()

    file_dialog = QtWidgets.QFileDialog()
    file_dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
    filename = QtWidgets.QFileDialog.getOpenFileName(file_dialog, "Select traktexport export file", "", "json(*json)")
    filename = filename[0]

    app.quit()

file = open(filename, 'r')
data = json.load(file)


ratings = {}
for item in data['ratings']:
    type = item['type']
    item_tmdb_id = item[type]['ids']['tmdb']
    ratings[item_tmdb_id] = item['rating']

if not os.path.exists('info.dict'):
    with open('info.dict', 'wb') as file2:
        pickle.dump(DotMap(), file2)

if not os.path.exists('json_data.json'):
    with open('json_data.json', 'w') as file2:
        dct = {"networks": {}, "studios": {}, "castlist": {}, "crewlist": {}, "lists": {}}
        json.dump(dct, file2)


info = pickle.load(open('info.dict', 'rb'))
info_copy = info.copy()

json_data = json.load(open('json_data.json', 'r'))
json_data_copy = deepcopy(json_data)

castlist = json_data['castlist']
crewlist = json_data['crewlist']
networks = json_data['networks']
studioslst = json_data['studios']
list_of_lists = json_data['lists']

name = data['profile']['name'].split(' ')[0]

joined_date = data['history'][-1]['watched_at'].split('T')[0]

# Creating Directories
os.makedirs('.cache', exist_ok=True)
os.makedirs('.cache/cast', exist_ok=True)
os.makedirs('.cache/crew', exist_ok=True)
os.makedirs('.cache/posters', exist_ok=True)
os.makedirs('.cache/studios', exist_ok=True)
os.makedirs('.cache/network_icons', exist_ok=True)
os.makedirs('.cache/posters/processed', exist_ok=True)

firstRun = False
