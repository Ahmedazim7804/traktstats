import os
import random
import pathlib
import itertools
from dotmap import DotMap
from datetime import datetime
from operator import itemgetter
from bubblechart import BubbleChart
from matplotlib import pyplot as plt
from PIL import Image, ImageDraw, ImageFont
from getData import getData, download_tmdb_image
from matplotlib.offsetbox import OffsetImage, AnnotationBbox


watched_movies, watched_episodes, watched_shows, len_ratings, len_lists, json_data, name, joined_date = getData()

studios_id_2_name = json_data['studios']
networks_id_2_name = json_data['networks']
castlist = json_data['castlist']
crewlist = json_data['crewlist']
list_of_lists = json_data['lists']


def sort_dict_by_key(dct, use_key_type=int, reverse=False):

    def get_key(key):
        key = key[0]

        if use_key_type is int:
            return int(key)
        elif use_key_type is str:
            return str(key)
        else:
            return key

    return {key: value for key, value in sorted(dct.items(), key=get_key, reverse=reverse)}


def sort_dict_by_value(dct, reverse=False):
    return {key: value for key, value in sorted(dct.items(), key=lambda x: x[1], reverse=reverse)}


def custom_sort_dict(dct, indexes, return_item_count=0, reverse=False):
    def get_key(array):
        key = array
        for index in indexes:
            key = key[index]

        return key

    if return_item_count != 0:
        return {key: value for key, value in sorted(dct.items(), key=get_key, reverse=reverse)[:return_item_count]}
    else:
        return {key: value for key, value in sorted(dct.items(), key=get_key, reverse=reverse)}


def human_time(mins):
    days = mins//1440
    hours = int(mins - days*1440)//60
    minutes = int(mins - days*1440 - hours*60)
    result = ("{}D ".format(days) if days else "") + \
    ("{}H ".format(hours) if hours else "") + \
    ("{}M ".format(minutes) if minutes else "")
    return result


def graph_post_processing(fig, ax, threshold=0):
    fig.patch.set_facecolor('black')
    ax.patch.set_facecolor('black')
    ax.tick_params(axis='x', colors='#999999')
    ax.tick_params(axis='y', colors='#999999')
    for axis in ['bottom', 'left']:
        ax.spines[axis].set_linewidth(1.5)
        ax.spines[axis].set_color('#999999')
    for bar in ax.containers:
        labels = [value if value > threshold else "" for value in bar.datavalues]
        ax.bar_label(bar, labels=labels, color='white')


def get_all_time_totals():
    plays = str(sum([movie.plays for movie in watched_movies.values()]) + sum([episode.plays for episode in watched_episodes.values()]))
    minutes = sum([movie.runtime for movie in watched_movies.values()]) + sum([episode.runtime for episode in watched_episodes.values()])
    hours = "%.2f" % (minutes/60)
    collected = "0"
    number_of_ratings = str(len_ratings)
    comments = "0"
    lists = str(len_lists)

    return DotMap({'plays': plays, 'hours': hours, 'collected': collected, 'number_of_ratings': number_of_ratings, 'comments': comments, 'lists': lists})


def get_path(filename, category, processed=False):
    if category == 'network':
        folder = 'network_icons'
    elif category == 'studios':
        folder = 'studios'

    path = (pathlib.Path('.cache') / folder / filename).with_suffix('.png')

    return path


def tvshow_stats():
    days = (datetime.now().date() - datetime.strptime(joined_date, "%Y-%m-%d").date()).days
    months = "%.2f" % (days / 30)
    years = "%.2f" % (days / 365)

    minutes = sum([episode.runtime for episode in watched_episodes.values()])
    hours = "%.2f" % (minutes / 60)
    hours_per_year = "%.2f" % (float(hours) / float(years))
    hours_per_month = "%.2f" % (float(hours) / float(months))
    hours_per_day = "%.2f" % (float(hours) / float(days))

    plays = sum([episode.plays for episode in watched_episodes.values()])
    plays_per_year = "%.2f" % (plays / float(years))
    plays_per_month = "%.2f" % (plays / float(months))
    plays_per_day = "%.2f" % (plays / float(days))

    return DotMap({'hours': hours, 'hours_per_year': hours_per_year, 'hours_per_month': hours_per_month, 'hours_per_day': hours_per_day,
                   'plays': str(plays),'plays_per_year': plays_per_year, 'plays_per_month': plays_per_month, 'plays_per_day': plays_per_day})


def tvshow_graphs():
    plays_per_date = {}
    plays_per_year = {}
    plays_per_month = {}

    for episode in watched_episodes.values():
        times = episode['time']
        for time in times:
            time = datetime.strptime(time.split('T')[0], "%Y-%m-%d")

            day = time.strftime("%a")
            month = time.strftime("%b")
            year = str(time.year)

            plays_per_date[day] = plays_per_date.get(day, 0) + 1
            plays_per_month[month] = plays_per_month.get(month, 0) + 1
            plays_per_year[year] = plays_per_year.get(year, 0) + 1

    first_year, last_year = itemgetter(0,-1)(sorted(plays_per_year.keys(), key=int))
    first_year, last_year = int(first_year), int(last_year)
    for year in range(first_year, last_year+1):
        year = str(year)
        if year not in plays_per_year.keys():
            plays_per_year[year] = 0

    plays_per_year = sort_dict_by_key(plays_per_year)

    fig1, ax1 = plt.subplots(1)
    fig2, ax2 = plt.subplots(1)
    fig3, ax3 = plt.subplots(1)

    ax1.bar(plays_per_year.keys(), plays_per_year.values(), color='white', align='center')
    ax2.bar(plays_per_month.keys(), plays_per_month.values(), color='white', align='center')
    ax3.bar(plays_per_date.keys(), plays_per_date.values(), color='white', align='center')

    graph_post_processing(fig1, ax1)
    graph_post_processing(fig2, ax2)
    graph_post_processing(fig3, ax3)

    return fig1, fig2, fig3


def top_tv_shows():

    sorted_watched_shows = {k: v for k,v in sorted(watched_shows.items(), key=lambda item: item[1]['plays'], reverse=True)}
    most_played_shows = {}
    for id, show in sorted_watched_shows.items():
        playtime = sum(i['runtime'] for i in watched_episodes.values() if i['tmdb_show_id'] == id)
        poster_url = show['poster']

        most_played_shows[id] = {'playtime': playtime, 'poster': poster_url}

    most_played_shows = {k: v for k,v in sorted(most_played_shows.items(), key=lambda item: item[1]['playtime'], reverse=True)}
    top_ten = dict(itertools.islice(most_played_shows.items(), 10))

    for id, item in top_ten.items():
        playtime, poster_url = item.values()
        top_ten[id]['playtime'] = human_time(playtime)
        top_ten[id]['poster'] = download_tmdb_image(url=poster_url, basepath='posters', filename=f"{id}", size='154')

    return top_ten, name, list_of_lists['trakt']['most_played_shows']


def tv_shows_stats2():
    tv_show_genres = {}
    tv_show_released_years = {}
    for show in watched_shows.values():

        title = show['title']
        release_year = str(show['released_year'])
        for genre in show['genres']:
            tv_show_genres[genre] = tv_show_genres.get(genre, 0) + 1
        tv_show_released_years[release_year] = tv_show_released_years.get(release_year, 0) + 1


    tv_show_released_years = sort_dict_by_key(tv_show_released_years)
    tv_show_genres = sort_dict_by_value(tv_show_genres, reverse=True)

    fig, ax = plt.subplots(1, figsize=(10, 10))
    ax.bar(tv_show_released_years.keys(), tv_show_released_years.values(), color='#999999', width=0.98, align='center')
    plt.xticks(rotation=40)
    fig.autofmt_xdate()
    fig.tight_layout(rect=[0, 0.2, 1, 0.8])
    graph_post_processing(fig, ax, 0)
    return tv_show_genres, fig


def tv_show_countries():
    twoletter_to_threeletter_country_code = {"BD": "BGD", "BE": "BEL", "BF": "BFA", "BG": "BGR", "BA": "BIH", "BB": "BRB", "WF": "WLF", "BL": "BLM", "BM": "BMU", "BN": "BRN", "BO": "BOL", "BH": "BHR", "BI": "BDI", "BJ": "BEN", "BT": "BTN", "JM": "JAM", "BV": "BVT", "BW": "BWA", "WS": "WSM", "BQ": "BES", "BR": "BRA", "BS": "BHS", "JE": "JEY", "BY": "BLR", "BZ": "BLZ", "RU": "RUS", "RW": "RWA", "RS": "SRB", "TL": "TLS", "RE": "REU", "TM": "TKM", "TJ": "TJK", "RO": "ROU", "TK": "TKL", "GW": "GNB", "GU": "GUM", "GT": "GTM", "GS": "SGS", "GR": "GRC", "GQ": "GNQ", "GP": "GLP", "JP": "JPN", "GY": "GUY", "GG": "GGY", "GF": "GUF", "GE": "GEO", "GD": "GRD", "GB": "GBR", "GA": "GAB", "SV": "SLV", "GN": "GIN", "GM": "GMB", "GL": "GRL", "GI": "GIB", "GH": "GHA", "OM": "OMN", "TN": "TUN", "JO": "JOR", "HR": "HRV", "HT": "HTI", "HU": "HUN", "HK": "HKG", "HN": "HND", "HM": "HMD", "VE": "VEN", "PR": "PRI", "PS": "PSE", "PW": "PLW", "PT": "PRT", "SJ": "SJM", "PY": "PRY", "IQ": "IRQ", "PA": "PAN", "PF": "PYF", "PG": "PNG", "PE": "PER", "PK": "PAK", "PH": "PHL", "PN": "PCN", "PL": "POL", "PM": "SPM", "ZM": "ZMB", "EH": "ESH", "EE": "EST", "EG": "EGY", "ZA": "ZAF", "EC": "ECU", "IT": "ITA", "VN": "VNM", "SB": "SLB", "ET": "ETH", "SO": "SOM", "ZW": "ZWE", "SA": "SAU", "ES": "ESP", "ER": "ERI", "ME": "MNE", "MD": "MDA", "MG": "MDG", "MF": "MAF", "MA": "MAR", "MC": "MCO", "UZ": "UZB", "MM": "MMR", "ML": "MLI", "MO": "MAC", "MN": "MNG", "MH": "MHL", "MK": "MKD", "MU": "MUS", "MT": "MLT", "MW": "MWI", "MV": "MDV", "MQ": "MTQ", "MP": "MNP", "MS": "MSR", "MR": "MRT", "IM": "IMN", "UG": "UGA", "TZ": "TZA", "MY": "MYS", "MX": "MEX", "IL": "ISR", "FR": "FRA", "IO": "IOT", "SH": "SHN", "FI": "FIN", "FJ": "FJI", "FK": "FLK", "FM": "FSM", "FO": "FRO", "NI": "NIC", "NL": "NLD", "NO": "NOR", "NA": "NAM", "VU": "VUT", "NC": "NCL", "NE": "NER", "NF": "NFK", "NG": "NGA", "NZ": "NZL", "NP": "NPL", "NR": "NRU", "NU": "NIU", "CK": "COK", "XK": "XKX", "CI": "CIV", "CH": "CHE", "CO": "COL", "CN": "CHN", "CM": "CMR", "CL": "CHL", "CC": "CCK", "CA": "CAN", "CG": "COG", "CF": "CAF", "CD": "COD", "CZ": "CZE", "CY": "CYP", "CX": "CXR", "CR": "CRI", "CW": "CUW", "CV": "CPV", "CU": "CUB", "SZ": "SWZ", "SY": "SYR", "SX": "SXM", "KG": "KGZ", "KE": "KEN", "SS": "SSD", "SR": "SUR", "KI": "KIR", "KH": "KHM", "KN": "KNA", "KM": "COM", "ST": "STP", "SK": "SVK", "KR": "KOR", "SI": "SVN", "KP": "PRK", "KW": "KWT", "SN": "SEN", "SM": "SMR", "SL": "SLE", "SC": "SYC", "KZ": "KAZ", "KY": "CYM", "SG": "SGP", "SE": "SWE", "SD": "SDN", "DO": "DOM", "DM": "DMA", "DJ": "DJI", "DK": "DNK", "VG": "VGB", "DE": "DEU", "YE": "YEM", "DZ": "DZA", "US": "USA", "UY": "URY", "YT": "MYT", "UM": "UMI", "LB": "LBN", "LC": "LCA", "LA": "LAO", "TV": "TUV", "TW": "TWN", "TT": "TTO", "TR": "TUR", "LK": "LKA", "LI": "LIE", "LV": "LVA", "TO": "TON", "LT": "LTU", "LU": "LUX", "LR": "LBR", "LS": "LSO", "TH": "THA", "TF": "ATF", "TG": "TGO", "TD": "TCD", "TC": "TCA", "LY": "LBY", "VA": "VAT", "VC": "VCT", "AE": "ARE", "AD": "AND", "AG": "ATG", "AF": "AFG", "AI": "AIA", "VI": "VIR", "IS": "ISL", "IR": "IRN", "AM": "ARM", "AL": "ALB", "AO": "AGO", "AQ": "ATA", "AS": "ASM", "AR": "ARG", "AU": "AUS", "AT": "AUT", "AW": "ABW", "IN": "IND", "AX": "ALA", "AZ": "AZE", "IE": "IRL", "ID": "IDN", "UA": "UKR", "QA": "QAT", "MZ": "MOZ"}
    countries = {}

    for show in watched_shows.keys():
        country = watched_shows[show]['country'].upper()
        country = twoletter_to_threeletter_country_code[country]

        countries[country] = countries.get(country, 0) + 1

    return countries, list(twoletter_to_threeletter_country_code.values())


def tv_show_networks():
    networks = {}

    for show in watched_shows.values():
        network = show['network']
        networks[network] = networks.get(network, 0) + 1

    networks = {k: v for k, v in sorted(networks.items(), key=lambda item: item[1], reverse=True)}
    network_icons = [get_path(network, 'network') for network in networks]
    network_labels = {id: networks_id_2_name[id] for id in networks}
    colors = ["#%06x" % random.randint(0, 0xFFFFFF) for i in networks.keys()]

    bubble_chart = BubbleChart(area=list(networks.values()), bubble_spacing=0.1)
    bubble_chart.collapse()

    fig, ax = plt.subplots(subplot_kw=dict(aspect="equal"))

    bubble_cords = bubble_chart.plot(ax, ids=list(networks.keys()), icons=network_icons, colors=colors)

    x = [i[0] for i in bubble_cords]
    y = [j[1] for j in bubble_cords]
    s = [k[2] for k in bubble_cords]
    ids = [l[3] for l in bubble_cords]

    scatter = plt.scatter(x=x, y=y, s=s, color="#FFFFFF", alpha=0)

    ax.axis("off")
    ax.relim()
    ax.autoscale_view()
    ax.set_title('Browser market share')

    graph_post_processing(fig, ax)

    annot = ax.annotate("", xy=(0, 0), xytext=(20, 20), textcoords="offset points", color='#e1dfdc',
                        bbox=dict(boxstyle="round", fc="w"),
                        arrowprops=dict(arrowstyle="->"), ha='center', va='center')

    annot.set_visible(False)

    def update_annot(ind):

        pos = scatter.get_offsets()[ind["ind"][0]]
        annot.xy = pos

        index = ind['ind'][0]
        network_id = ids[index]
        network_name = network_labels[network_id]
        shows = networks[network_id]

        text = f"$\\bf{network_name}$\n{shows} {'shows' if shows > 1 else 'show'}"

        annot.set_text(text)
        annot.get_bbox_patch().set_facecolor("#010101")
        annot.get_bbox_patch().set_edgecolor('#635d51')
        annot.get_bbox_patch().set_alpha(0.8)

    def hover(event):
        vis = annot.get_visible()
        if event.inaxes == ax:
            cont, ind = scatter.contains(event)
            if cont:
                update_annot(ind)
                annot.set_visible(True)
                fig.canvas.draw_idle()
            else:
                if vis:
                    annot.set_visible(False)
                    fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", hover)

    return fig


def tv_list_progress():

    fig = plt.figure(facecolor='black', figsize=(10,10))

    ax1 = fig.add_subplot(131)
    ax2 = fig.add_subplot(132)
    ax3 = fig.add_subplot(133)

    for ax, name, title in zip([ax1, ax2, ax3], ['trakt', 'imdb', 'rollingstone'], ['Trakt', 'IMDB', 'Rolling Stone\'s']):

        lst = list_of_lists['shows'][name]
        colors = ['#ea212d', '#222222']
        wool = 0    # wool = Watched out of list
        total = len(lst)

        for show in watched_shows.keys():
            if show in lst:
                wool += 1

        perc = '{:.1f}%'.format((wool / total) * 100)

        centre_circle = plt.Circle((0, 0), 0.80, fc='black')

        text = f'{name.upper()} Top 250\n{perc}%\nWatched {wool} of {total}'

        ax.pie([wool, 250 - wool], labels=['IMDB', 'others'], autopct=lambda p: '{:.0f}%'.format(p), colors=colors)
        ax.add_artist(centre_circle)
        ax.text(0, 0.17, f'{title} Top {total}', ha='center', va='center', fontsize=9, color='#ffffff')
        ax.text(0, 0.10, '_' * 15, ha='center', va='center', fontsize=16, color='#6b6358')
        ax.text(0.05, -0.20, perc, ha='center', va='center', fontsize=24, color='#ffffff')
        ax.text(0, -0.43, f'Watched {wool} OF {total}', ha='center', va='center', fontsize=9,color='#606060')

        im = plt.imread(pathlib.Path('resources') / f"{name}.png")
        imagebox = OffsetImage(im, zoom=72 / fig.dpi)
        imagebox.image.axes = ax
        ab = AnnotationBbox(imagebox, (0, 0.45), xycoords='data', frameon=False)
        ax.add_artist(ab)


    plt.subplots_adjust(left=0,
                        right=0.999,
                        wspace=0,
                        hspace=0)

    #plt.subplot_tool()
    return fig


def highest_rated_tv():
    processed_images = [os.path.splitext(i)[0] for i in os.listdir('.cache/posters/processed')]
    font_path = str(pathlib.Path('resources/Lato-Black.ttf'))

    def process_image(filename, filepath, extension, rating):
        save_path = (pathlib.Path('.cache/posters/processed') / filename).with_suffix(extension)
        save_path = str(save_path)

        if filename not in processed_images:

            print(f'Processing Image {filename}')
            image = Image.open(filepath)
            draw = ImageDraw.Draw(image)

            draw.polygon([(0, 0), (0, 35), (35, 0)], fill=(255, 0, 0))

            if rating == 10:
                font = ImageFont.truetype(font_path, 18)
                draw.text((0, 2.2), str(rating), fill=(255, 255, 255), font=font)
            else:
                font = ImageFont.truetype(font_path, 20)
                draw.text((3, 2.0), str(rating), fill=(255, 255, 255), font=font)

            image.save(save_path, format='JPEG', quality=100)
            image.close()

        return save_path

    shows = {}
    all_ratings = {}

    for show in watched_shows.values():
        id = show['id']
        title = show['title']
        rating = show['rating']
        url = show['poster']

        if not rating:
            continue

        shows[id] = [rating, url, title]
        all_ratings[rating] = all_ratings.get(rating, 0) + 1

    shows = custom_sort_dict(dct=shows, indexes=[1, 0], return_item_count=10, reverse=True)
    all_ratings = sort_dict_by_key(all_ratings, use_key_type=int, reverse=True)

    highest_rated = {}
    for show in shows.items():
        id, (rating, url, title) = show

        file_path = download_tmdb_image(url=url, basepath='posters', filename=f"{id}", size='154')
        ext = file_path[-4:]
        poster_path = process_image(id, file_path, ext, rating)

        highest_rated[id] = poster_path

    return highest_rated, all_ratings


def movies_stats():
    days = (datetime.now().date() - datetime.strptime(joined_date, "%Y-%m-%d").date()).days
    months = "%.2f" % (days / 30)
    years = "%.2f" % (days / 365)

    minutes = sum([movie.runtime for movie in watched_movies.values()])
    hours = "%.2f" % (minutes / 60)
    hours_per_year = "%.2f" % (float(hours) / float(years))
    hours_per_month = "%.2f" % (float(hours) / float(months))
    hours_per_day = "%.2f" % (float(hours) / float(days))

    plays = sum([movie.plays for movie in watched_movies.values()])
    plays_per_year = "%.2f" % (plays / float(years))
    plays_per_month = "%.2f" % (plays / float(months))
    plays_per_day = "%.2f" % (plays / float(days))

    return DotMap({'hours': hours, 'hours_per_year': hours_per_year, 'hours_per_month': hours_per_month,
                   'hours_per_day': hours_per_day,
                   'plays': str(plays), 'plays_per_year': plays_per_year, 'plays_per_month': plays_per_month,
                   'plays_per_day': plays_per_day})


def movies_graphs():
    plays_per_date = {}
    plays_per_year = {}
    plays_per_month = {}

    for movie in watched_movies.values():
        times = movie['time']
        for time in times:
            time = datetime.strptime(time.split('T')[0], "%Y-%m-%d")

            day = time.strftime("%a")
            month = time.strftime("%b")
            year = str(time.year)

            plays_per_date[day] = plays_per_date.get(day, 0) + 1
            plays_per_month[month] = plays_per_month.get(month, 0) + 1
            plays_per_year[year] = plays_per_year.get(year, 0) + 1

    first_year, last_year = itemgetter(0, -1)(sorted(plays_per_year.keys(), key=int))
    first_year, last_year = int(first_year), int(last_year)
    for year in range(first_year, last_year + 1):
        year = str(year)
        if year not in plays_per_year.keys():
            plays_per_year[year] = 0

    plays_per_year = sort_dict_by_key(plays_per_year)

    fig1, ax1 = plt.subplots(1)
    fig2, ax2 = plt.subplots(1)
    fig3, ax3 = plt.subplots(1)

    ax1.bar(plays_per_year.keys(), plays_per_year.values(), color='white', align='center')
    ax2.bar(plays_per_month.keys(), plays_per_month.values(), color='white', align='center')
    ax3.bar(plays_per_date.keys(), plays_per_date.values(), color='white', align='center')

    graph_post_processing(fig1, ax1)
    graph_post_processing(fig2, ax2)
    graph_post_processing(fig3, ax3)

    return fig1, fig2, fig3


def top_movies():
    sorted_watched_movies = {k: v for k, v in
                            sorted(watched_movies.items(), key=lambda item: item[1]['plays'], reverse=True)}
    most_played_movies = {}
    for id, movie in sorted_watched_movies.items():
        playtime = movie['plays'] * movie['runtime']
        poster_url = 'https://image.tmdb.org/t/p/w154' + movie['poster']

        most_played_movies[id] = {'playtime': playtime, 'poster': poster_url}

    most_played_movies = {k: v for k, v in
                         sorted(most_played_movies.items(), key=lambda item: item[1]['playtime'], reverse=True)}
    top_ten = dict(itertools.islice(most_played_movies.items(), 10))

    for id, item in top_ten.items():
        playtime, poster_url = item.values()
        top_ten[id]['playtime'] = human_time(playtime)
        top_ten[id]['poster'] = download_tmdb_image(url=poster_url, basepath='posters', filename=f"{id}", size='154')

    return top_ten, name, list_of_lists['trakt']['most_played_movies']


def movies_stats2():
    movie_genres = {}
    movie_released_years = {}
    for movie in watched_movies.values():
        title = movie['title']
        release_year = str(movie['released_year'])
        for genre in movie['genres']:
            movie_genres[genre] = movie_genres.get(genre, 0) + 1
        movie_released_years[release_year] = movie_released_years.get(release_year, 0) + 1


    movie_released_years = sort_dict_by_key(movie_released_years)
    movie_genres = sort_dict_by_value(movie_genres, reverse=True)

    fig, ax = plt.subplots(1, figsize=(10, 10))
    ax.bar(movie_released_years.keys(), movie_released_years.values(), color='#999999', width=0.98, align='center')
    plt.xticks(rotation=40)
    fig.autofmt_xdate()
    fig.tight_layout(rect=[0, 0.2, 1, 0.8])
    graph_post_processing(fig, ax, 0)
    return movie_genres, fig


def movies_countries():
    twoletter_to_threeletter_country_code = {"BD": "BGD", "BE": "BEL", "BF": "BFA", "BG": "BGR", "BA": "BIH", "BB": "BRB", "WF": "WLF", "BL": "BLM", "BM": "BMU", "BN": "BRN", "BO": "BOL", "BH": "BHR", "BI": "BDI", "BJ": "BEN", "BT": "BTN", "JM": "JAM", "BV": "BVT", "BW": "BWA", "WS": "WSM", "BQ": "BES", "BR": "BRA", "BS": "BHS", "JE": "JEY", "BY": "BLR", "BZ": "BLZ", "RU": "RUS", "RW": "RWA", "RS": "SRB", "TL": "TLS", "RE": "REU", "TM": "TKM", "TJ": "TJK", "RO": "ROU", "TK": "TKL", "GW": "GNB", "GU": "GUM", "GT": "GTM", "GS": "SGS", "GR": "GRC", "GQ": "GNQ", "GP": "GLP", "JP": "JPN", "GY": "GUY", "GG": "GGY", "GF": "GUF", "GE": "GEO", "GD": "GRD", "GB": "GBR", "GA": "GAB", "SV": "SLV", "GN": "GIN", "GM": "GMB", "GL": "GRL", "GI": "GIB", "GH": "GHA", "OM": "OMN", "TN": "TUN", "JO": "JOR", "HR": "HRV", "HT": "HTI", "HU": "HUN", "HK": "HKG", "HN": "HND", "HM": "HMD", "VE": "VEN", "PR": "PRI", "PS": "PSE", "PW": "PLW", "PT": "PRT", "SJ": "SJM", "PY": "PRY", "IQ": "IRQ", "PA": "PAN", "PF": "PYF", "PG": "PNG", "PE": "PER", "PK": "PAK", "PH": "PHL", "PN": "PCN", "PL": "POL", "PM": "SPM", "ZM": "ZMB", "EH": "ESH", "EE": "EST", "EG": "EGY", "ZA": "ZAF", "EC": "ECU", "IT": "ITA", "VN": "VNM", "SB": "SLB", "ET": "ETH", "SO": "SOM", "ZW": "ZWE", "SA": "SAU", "ES": "ESP", "ER": "ERI", "ME": "MNE", "MD": "MDA", "MG": "MDG", "MF": "MAF", "MA": "MAR", "MC": "MCO", "UZ": "UZB", "MM": "MMR", "ML": "MLI", "MO": "MAC", "MN": "MNG", "MH": "MHL", "MK": "MKD", "MU": "MUS", "MT": "MLT", "MW": "MWI", "MV": "MDV", "MQ": "MTQ", "MP": "MNP", "MS": "MSR", "MR": "MRT", "IM": "IMN", "UG": "UGA", "TZ": "TZA", "MY": "MYS", "MX": "MEX", "IL": "ISR", "FR": "FRA", "IO": "IOT", "SH": "SHN", "FI": "FIN", "FJ": "FJI", "FK": "FLK", "FM": "FSM", "FO": "FRO", "NI": "NIC", "NL": "NLD", "NO": "NOR", "NA": "NAM", "VU": "VUT", "NC": "NCL", "NE": "NER", "NF": "NFK", "NG": "NGA", "NZ": "NZL", "NP": "NPL", "NR": "NRU", "NU": "NIU", "CK": "COK", "XK": "XKX", "CI": "CIV", "CH": "CHE", "CO": "COL", "CN": "CHN", "CM": "CMR", "CL": "CHL", "CC": "CCK", "CA": "CAN", "CG": "COG", "CF": "CAF", "CD": "COD", "CZ": "CZE", "CY": "CYP", "CX": "CXR", "CR": "CRI", "CW": "CUW", "CV": "CPV", "CU": "CUB", "SZ": "SWZ", "SY": "SYR", "SX": "SXM", "KG": "KGZ", "KE": "KEN", "SS": "SSD", "SR": "SUR", "KI": "KIR", "KH": "KHM", "KN": "KNA", "KM": "COM", "ST": "STP", "SK": "SVK", "KR": "KOR", "SI": "SVN", "KP": "PRK", "KW": "KWT", "SN": "SEN", "SM": "SMR", "SL": "SLE", "SC": "SYC", "KZ": "KAZ", "KY": "CYM", "SG": "SGP", "SE": "SWE", "SD": "SDN", "DO": "DOM", "DM": "DMA", "DJ": "DJI", "DK": "DNK", "VG": "VGB", "DE": "DEU", "YE": "YEM", "DZ": "DZA", "US": "USA", "UY": "URY", "YT": "MYT", "UM": "UMI", "LB": "LBN", "LC": "LCA", "LA": "LAO", "TV": "TUV", "TW": "TWN", "TT": "TTO", "TR": "TUR", "LK": "LKA", "LI": "LIE", "LV": "LVA", "TO": "TON", "LT": "LTU", "LU": "LUX", "LR": "LBR", "LS": "LSO", "TH": "THA", "TF": "ATF", "TG": "TGO", "TD": "TCD", "TC": "TCA", "LY": "LBY", "VA": "VAT", "VC": "VCT", "AE": "ARE", "AD": "AND", "AG": "ATG", "AF": "AFG", "AI": "AIA", "VI": "VIR", "IS": "ISL", "IR": "IRN", "AM": "ARM", "AL": "ALB", "AO": "AGO", "AQ": "ATA", "AS": "ASM", "AR": "ARG", "AU": "AUS", "AT": "AUT", "AW": "ABW", "IN": "IND", "AX": "ALA", "AZ": "AZE", "IE": "IRL", "ID": "IDN", "UA": "UKR", "QA": "QAT", "MZ": "MOZ"}
    countries = {}

    for movie in watched_movies.keys():
        country = watched_movies[movie]['country'].upper()
        country = twoletter_to_threeletter_country_code[country]

        countries[country] = countries.get(country, 0) + 1

    return countries, list(twoletter_to_threeletter_country_code.values())


def movie_studios():
    all_studios = {}

    for movie in watched_movies.values():

        studios = movie['studios']
        for studio in studios:
            all_studios[studio] = all_studios.get(studio, 0) + 1

    all_studios = {k: v for k, v in sorted(all_studios.items(), key=lambda item: item[1], reverse=True)}
    studios_icon = [get_path(studio, 'studios') for studio in all_studios]
    studios_label = {studio: studios_id_2_name[studio] for studio in all_studios}
    colors = ["#%06x" % random.randint(0, 0xFFFFFF) for i in all_studios.keys()]

    bubble_chart = BubbleChart(area=list(all_studios.values()), bubble_spacing=0.1)
    bubble_chart.collapse()

    fig, ax = plt.subplots(subplot_kw=dict(aspect="equal"))

    bubble_cords = bubble_chart.plot(ax, ids=list(all_studios.keys()), icons=studios_icon, colors=colors)

    x = [i[0] for i in bubble_cords]
    y = [j[1] for j in bubble_cords]
    s = [k[2] for k in bubble_cords]
    ids = [l[3] for l in bubble_cords]

    scatter = plt.scatter(x=x, y=y, s=s, color="#FFFFFF", alpha=0)

    ax.axis("off")
    ax.relim()
    ax.autoscale_view()
    ax.set_title('Browser market share')

    graph_post_processing(fig, ax)

    annot = ax.annotate("", xy=(0, 0), xytext=(20, 20), textcoords="offset points", color='#e1dfdc',
                        bbox=dict(boxstyle="round", fc="w"),
                        arrowprops=dict(arrowstyle="->"), ha='center', va='center')

    annot.set_visible(False)

    def update_annot(ind):

        pos = scatter.get_offsets()[ind["ind"][0]]
        annot.xy = pos

        index = ind['ind'][0]
        studio_id = ids[index]
        studio_name = studios_label[studio_id]
        shows = all_studios[studio_id]

        text = f"$\\bf{studio_name}$\n{shows} {'shows' if shows > 1 else 'show'}"

        annot.set_text(text)
        annot.get_bbox_patch().set_facecolor("#010101")
        annot.get_bbox_patch().set_edgecolor('#635d51')
        annot.get_bbox_patch().set_alpha(0.8)

    def hover(event):
        vis = annot.get_visible()
        if event.inaxes == ax:
            cont, ind = scatter.contains(event)
            if cont:
                update_annot(ind)
                annot.set_visible(True)
                fig.canvas.draw_idle()
            else:
                if vis:
                    annot.set_visible(False)
                    fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", hover)

    return fig


def movie_list_progress():
    fig = plt.figure(facecolor='black', figsize=(10, 10))

    ax1 = fig.add_subplot(131)
    ax2 = fig.add_subplot(132)
    ax3 = fig.add_subplot(133)

    for ax, name, title in zip([ax1, ax2, ax3], ['trakt', 'imdb', 'reddit'],
                               ['Trakt', 'IMDB', 'Reddit']):

        lst = list_of_lists['movies'][name]
        colors = ['#ea212d', '#222222']
        wool = 0  # wool = Watched out of list
        total = len(lst)

        for movie in watched_movies.keys():
            if movie in lst:
                wool += 1

        perc = '{:.1f}%'.format((wool / total) * 100)

        centre_circle = plt.Circle((0, 0), 0.80, fc='black')

        text = f'{name.upper()} Top 250\n{perc}%\nWatched {wool} of {total}'

        ax.pie([wool, 250 - wool], labels=['IMDB', 'others'], autopct=lambda p: '{:.0f}%'.format(p), colors=colors)
        ax.add_artist(centre_circle)
        ax.text(0, 0.17, f'{title} Top {total}', ha='center', va='center', fontsize=9, color='#ffffff')
        ax.text(0, 0.10, '_' * 15, ha='center', va='center', fontsize=16, color='#6b6358')
        ax.text(0.05, -0.20, perc, ha='center', va='center', fontsize=24, color='#ffffff')
        ax.text(0, -0.43, f'Watched {wool} OF {total}', ha='center', va='center', fontsize=9, color='#606060')

        im = plt.imread(pathlib.Path('resources') / f"{name}.png")
        imagebox = OffsetImage(im, zoom=72 / fig.dpi)
        imagebox.image.axes = ax
        ab = AnnotationBbox(imagebox, (0, 0.45), xycoords='data', frameon=False)
        ax.add_artist(ab)

    plt.subplots_adjust(left=0,
                        right=0.999,
                        wspace=0,
                        hspace=0)

    # plt.subplot_tool()
    return fig


def highest_rated_movies():
    processed_images = [os.path.splitext(i)[0] for i in os.listdir('.cache/posters/processed')]
    font_path = str(pathlib.Path('resources/Lato-Black.ttf'))

    def process_image(filename, filepath, extension, rating):
        save_path = (pathlib.Path('.cache/posters/processed') / filename).with_suffix(extension)
        save_path = str(save_path)

        if filename not in processed_images:

            print(f'Processing Image {filename}')
            image = Image.open(filepath)
            draw = ImageDraw.Draw(image)

            draw.polygon([(0, 0), (0, 35), (35, 0)], fill=(255, 0, 0))

            if rating == 10:
                font = ImageFont.truetype(font_path, 18)
                draw.text((0, 2.2), str(rating), fill=(255, 255, 255), font=font)
            else:
                font = ImageFont.truetype(font_path, 20)
                draw.text((3, 2.0), str(rating), fill=(255, 255, 255), font=font)

            image.save(save_path, format='JPEG', quality=100)
            image.close()

        return save_path

    movies = {}
    all_ratings = {}

    for movie in watched_movies.values():
        id = movie['id']
        title = movie['title']
        rating = movie['rating']
        url = movie['poster']

        if not rating:
            continue

        movies[id] = [rating, url, title]
        all_ratings[rating] = all_ratings.get(rating, 0) + 1

    movies = custom_sort_dict(dct=movies, indexes=[1, 0], return_item_count=10, reverse=True)
    all_ratings = sort_dict_by_key(all_ratings, use_key_type=int, reverse=True)

    highest_rated = {}
    for movie in movies.items():
        id, (rating, url, title) = movie

        file_path = download_tmdb_image(url=url, basepath='posters', filename=f"{id}", size='154')
        ext = file_path[-4:]
        poster_path = process_image(id, file_path, ext, rating)

        highest_rated[id] = poster_path

    return highest_rated, all_ratings


def most_watched_cast():
    actors = {}
    actress = {}
    non_binary = {}

    for movie in watched_movies.values():
        cast, movie_id, title, year = itemgetter('cast', 'id', 'title', 'released_year')(movie)
        movie_id = str(movie_id)

        for id in cast:
            name, gender_id, url = itemgetter('name', 'gender', 'image')(castlist[str(id)])

            if not url:
                continue

            if gender_id == 1:
                cast = actress
            elif gender_id == 2:
                cast = actors
            elif gender_id == 3:
                cast = non_binary
            else:
                continue

            if id not in cast.keys():
                cast[id] = {}

            person = cast[id]

            if 'name' not in person.keys():
                person['name'] = name

            if 'image' not in person.keys():
                person['image'] = url

            if 'movies' not in person.keys():
                person['movies'] = {}

            person['movies'][movie_id] = {'title': title, 'year': year}

    for episode in watched_episodes.values():
        cast, show_id, title, year = itemgetter('cast', 'tmdb_show_id', 'show', 'released_year')(episode)
        show_id = str(show_id)
        for id in cast:
            name, gender_id, url = itemgetter('name', 'gender', 'image')(castlist[str(id)])

            if not url:
                continue

            if gender_id == 1:
                cast = actress
            elif gender_id == 2:
                cast = actors
            else:
                cast = non_binary

            if id not in cast.keys():
                cast[id] = {}

            person = cast[id]

            if 'name' not in person.keys():
                person['name'] = name

            if 'image' not in person.keys():
                person['image'] = url

            if 'shows' not in person.keys():
                person['shows'] = {}

            if show_id not in person['shows'].keys():
                person['shows'][show_id] = {'title': title, 'episode': 0}

            person['shows'][show_id]['episode'] = person['shows'][show_id].get('episode', 0) + 1


    # Getting Top 100

    def key_to_sort(array):
        array = array[1]
        key = 0
        key += len(array.get('movies', []))
        key += len(array.get('shows', []))

        return key

    actors = sorted(actors.items(), key=key_to_sort, reverse=True)[:20]
    actress = sorted(actress.items(), key=key_to_sort, reverse=True)[:20]
    non_binary = sorted(non_binary.items(), key=key_to_sort, reverse=True)[:20]

    for lst in [actors, actress, non_binary]:
        for actor in lst:
            id, url = actor[0], actor[1]['image']
            image = download_tmdb_image(url=url, basepath='cast/', filename=f"{id}", size='154')
            actor[1]['image'] = image

    return actress, actors, non_binary


def most_watched_crew():
    crews = {'Director': {}, 'Writer': {}}

    for movie in watched_movies.values():
        movie_id, title, year = itemgetter('id', 'title', 'released_year')(movie)
        for job in movie['crew'].keys():
            for crew in movie['crew'][job]:
                name, url = itemgetter('name', 'image')(crewlist[str(crew)])

                if not url:
                    continue

                if crew not in crews[job].keys():
                    crews[job][crew] = {'name': name, 'image': url}

                if 'movies' not in crews[job][crew].keys():
                    crews[job][crew]['movies'] = {}

                crews[job][crew]['movies'][movie_id] = {'title': title, 'year': year}

    for episode in watched_episodes.values():
        show_id, title = itemgetter('tmdb_show_id', 'show')(episode)

        for job in episode['crew'].keys():
            for crew in episode['crew'][job]:
                name, url = itemgetter('name', 'image')(crewlist[str(crew)])

                if not url:
                    continue

                if crew not in crews[job].keys():
                    crews[job][crew] = {'name': name, 'image': url}

                if 'shows' not in crews[job][crew].keys():
                    crews[job][crew]['shows'] = {}

                if show_id not in crews[job][crew]['shows']:
                    crews[job][crew]['shows'][show_id] = {'title': title, 'episodes': 0}

                crews[job][crew]['shows'][show_id]['episodes'] = crews[job][crew]['shows'][show_id].get('episodes', 0) + 1

    all_directors, all_writers = crews.values()

    def key_to_sort(array):
        array = array[1]
        key = 0
        key += len(array.get('movies', []))
        key += len(array.get('shows', []))

        return key

    all_directors = sorted(all_directors.items(), key=key_to_sort, reverse=True)[:20]
    all_writers = sorted(all_writers.items(), key=key_to_sort, reverse=True)[:20]

    for lst in [all_directors, all_writers]:
        for crew in lst:
            id, url = crew[0], crew[1]['image']
            image = download_tmdb_image(url=url, basepath='crew/', filename=f"{id}", size='154')
            crew[1]['image'] = image

    return all_directors, all_writers