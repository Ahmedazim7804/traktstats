import sys
import random
import pathlib
import parseData
import plotly.graph_objects as go
from PyQt5 import uic
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWebEngineWidgets import QWebEngineView


stylesheet = """
    QWidget {
        background-color: black;
    }

    QScrollBar:horizontal
    {
        height: 15px;
        margin: 3px 15px 3px 15px;
        border: 1px transparent #2A2929;
        border-radius: 4px;
        background-color: #2A2929;
    }

    QScrollBar::handle:horizontal
    {
        background-color: gray;
        min-width: 5px;
        border-radius: 4px;
    }

    QScrollBar::add-line:horizontal
    {
        margin: 0px 3px 0px 3px;
        border-image: url(:/qss_icons/rc/right_arrow_disabled.png);
        width: 10px;
        height: 10px;
        subcontrol-position: right;
        subcontrol-origin: margin;
    }

    QScrollBar::sub-line:horizontal
    {
        margin: 0px 3px 0px 3px;
        border-image: url(:/qss_icons/rc/left_arrow_disabled.png);
        height: 10px;
        width: 10px;
        subcontrol-position: left;
        subcontrol-origin: margin;
    }

    QScrollBar::add-line:horizontal:hover,QScrollBar::add-line:horizontal:on
    {
        border-image: url(:/qss_icons/rc/right_arrow.png);
        height: 10px;
        width: 10px;
        subcontrol-position: right;
        subcontrol-origin: margin;
    }


    QScrollBar::sub-line:horizontal:hover, QScrollBar::sub-line:horizontal:on
    {
        border-image: url(:/qss_icons/rc/left_arrow.png);
        height: 10px;
        width: 10px;
        subcontrol-position: left;
        subcontrol-origin: margin;
    }

    QScrollBar::up-arrow:horizontal, QScrollBar::down-arrow:horizontal
    {
        background: none;
    }


    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal
    {
        background: none;
    }

    QScrollBar:vertical
    {
        background-color: #2A2929;
        width: 15px;
        margin: 15px 3px 15px 3px;
        border: 1px transparent #2A2929;
        border-radius: 4px;
    }

    QScrollBar::handle:vertical
    {
        background-color: gray;
        min-height: 5px;
        border-radius: 4px;
    }

    QScrollBar::sub-line:vertical
    {
        margin: 3px 0px 3px 0px;
        border-image: url(:/qss_icons/rc/up_arrow_disabled.png);
        height: 10px;
        width: 10px;
        subcontrol-position: top;
        subcontrol-origin: margin;
    }

    QScrollBar::add-line:vertical
    {
        margin: 3px 0px 3px 0px;
        border-image: url(:/qss_icons/rc/down_arrow_disabled.png);
        height: 10px;
        width: 10px;
        subcontrol-position: bottom;
        subcontrol-origin: margin;
    }

    QScrollBar::sub-line:vertical:hover,QScrollBar::sub-line:vertical:on
    {
        border-image: url(:/qss_icons/rc/up_arrow.png);
        height: 10px;
        width: 10px;
        subcontrol-position: top;
        subcontrol-origin: margin;
    }

    QScrollBar::add-line:vertical:hover, QScrollBar::add-line:vertical:on
    {
        border-image: url(:/qss_icons/rc/down_arrow.png);
        height: 10px;
        width: 10px;
        subcontrol-position: bottom;
        subcontrol-origin: margin;
    }

    QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical
    {
        background: none;
    }

    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical
    {
        background: none;
    }
"""


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setLayout(QtWidgets.QVBoxLayout())
        self.setStyleSheet(stylesheet)

        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter)
        self.scrollWidget = QtWidgets.QWidget()
        self.scrollWidget.setLayout(QtWidgets.QVBoxLayout())
        self.scrollArea.setAutoFillBackground(True)
        self.scrollArea.setMinimumSize(1024, 768)
        self.scrollArea.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.scrollArea.setFrameShape(QtWidgets.QFrame.Box)
        self.scrollArea.setWidgetResizable(True)

        pages = []
        pages.insert(0, self.page1())
        pages.insert(1, self.page2())
        pages.insert(2, self.page3())
        pages.insert(3, self.page4())
        pages.insert(4, self.page5())
        pages.insert(5, self.page6())
        pages.insert(6, self.page7())
        pages.insert(7, self.page8())

        for page in pages:
            page.setMinimumWidth(self.scrollArea.minimumWidth())
            page.setMinimumHeight(self.scrollArea.minimumHeight())
            self.scrollWidget.layout().addWidget(page)

        self.scrollArea.setWidget(self.scrollWidget)
        self.layout().addWidget(self.scrollArea)

    def page1(self):
        page = uic.loadUi("movies_page1.ui")
        data = parseData.movies_stats()

        page.hours.setText(data.hours)
        page.hours_per_year.setText(data.hours_per_year)
        page.hours_per_month.setText(data.hours_per_month)
        page.hours_per_day.setText(data.hours_per_day)
        page.plays.setText(data.plays)
        page.plays_per_year.setText(data.plays_per_year)
        page.plays_per_month.setText(data.plays_per_month)
        page.plays_per_day.setText(data.plays_per_day)
        return page

    def page2(self):
        graph1, graph2, graph3 = parseData.movies_graphs()
        page = uic.loadUi("movies_page2.ui")
        page.graph1.setupUi(graph1)
        page.graph2.setupUi(graph2)
        page.graph3.setupUi(graph3)

        return page

    def page3(self):
        top_movies, name, most_played_movies = parseData.top_movies()

        page = uic.loadUi("movies_page3.ui")

        logo_widget = page.findChild(QtWidgets.QLabel, 'logo')
        logo = QtGui.QPixmap(str(pathlib.Path('resources/traktlogo.png')))
        logo_widget.setPixmap(logo)

        title = page.label
        title.setText(f"{name.upper()}'s Top Shows")
        
        posters = [top_movies[show]['poster'] for show in top_movies]
        playtimes = [top_movies[show]['playtime'] for show in top_movies]

        n = 1
        for poster, playtime in zip(posters, playtimes):

            poster_widget = page.findChild(QtWidgets.QLabel, f'poster{n}')
            playtime_widget = page.findChild(QtWidgets.QLabel, f'playtime{n}')
            playtime_widget.setStyleSheet('color: white;')

            poster_widget.setPixmap(QtGui.QPixmap(poster).scaled(119, 178, transformMode=QtCore.Qt.SmoothTransformation, aspectRatioMode=QtCore.Qt.KeepAspectRatio))
            poster_widget.setScaledContents(True)
            playtime_widget.setText(str(playtime))

            n += 1

        for n, id in enumerate(most_played_movies.keys(), 1):

            show_title_widget = page.findChild(QtWidgets.QLabel, f"moviename{n}")
            plays_widget = page.findChild(QtWidgets.QLabel, f"plays{n}")

            movie_title = most_played_movies[id]['movie']['title']

            plays = most_played_movies[id]['play_count']

            if plays // 1000000:
                plays_label = '{:.1f}M PLAYS'.format(plays / 1000000)
            else:
                plays_label = '{:.0f}K PLAYS'.format(plays / 1000)

            show_title_widget.setText(movie_title)
            plays_widget.setText(plays_label)

        return page

    def page4(self):
        genres, graph = parseData.movies_stats2()
        page = uic.loadUi("movies_page4.ui")

        grid = page.findChild(QtWidgets.QGridLayout, 'grid')
        richtext = QtCore.QCoreApplication.translate

        count = 0
        total_genres = sum(genres.values())
        for genre, value in genres.items():
            color = tuple(random.choices(range(256), k=3))
            perc = '{:.0f}%'.format((value / total_genres) * 100)

            box = QtWidgets.QLabel(perc)
            box.setAlignment(QtCore.Qt.AlignCenter)
            box_stylesheet = f""".QLabel {{background-color: rgb{color}; color: rgb{color}; font-size: 13px;}} .QLabel:hover {{color: white;}}"""
            box.setStyleSheet(box_stylesheet)

            grid.addWidget(box, 1, count)

            line = QtWidgets.QFrame()
            line.setFrameShape(QtWidgets.QFrame.VLine | QtWidgets.QFrame.Sunken)
            line.setStyleSheet(f"background-color: rgb{color}; color: rgb{color};")

            label = QtWidgets.QLabel()
            label.setText(richtext("HOME",
                                   f"<html><head/><body><p style='margin-bottom:0; font-weight:600;'>{genre}</p><p style='margin : 0; padding-top:0; font-size:7pt;'>{value} MOVIES</p></body></html>"))
            label.setStyleSheet(f"padding-left: 5; background-color: black; color: white; font-weight: bold;")

            group = QtWidgets.QHBoxLayout()
            group.addWidget(line)
            group.addWidget(label)

            if count % 2 == 0:
                grid.addLayout(group, 0, count, 1, 2)
            else:
                grid.addLayout(group, 2, count, 1, 2)

            count += 1

        page.graph.setupUi(graph)

        return page

    def page5(self):
        page = uic.loadUi("movies_page5.ui")

        data, countries = parseData.movies_countries()

        values = []
        colorscales = [[0, "#333333"], [1, f"rgba(0, 160, 223, 1)"]]
        for country in countries:
            if country in data:
                value = data[country]
                values.append(value)
            else:
                values.append(0)

        max_value = max(values)
        min_value = min(values)
        for i in values:
            alpha = (((i - min_value)/(max_value-min_value)) * (1-0.3)) + 0.3  # NORMALIZE VALUES TO RANGE 0.3 to 1
            colorscale = [alpha, f"rgba(0, 160, 223, {alpha})"]
            if alpha and colorscale not in colorscales:
                colorscales.append(colorscale)

        colorscales = sorted(colorscales, key=lambda x: x[0])

        fig = go.Figure(data=go.Choropleth(
            locations=countries,
            z=values,
            colorscale=colorscales,
            marker_line_color="black",
            marker_line_width=0.24,
        ),
            layout=dict(paper_bgcolor="black",
                        geo=dict(bgcolor="#000000"),
                        margin=dict(l=0, r=0, t=25, b=0),
                        xaxis_showgrid=False,
                        yaxis_showgrid=False
                        ),
        )
        fig.update_geos(
            showlakes=False,
            showland=False,
            showcountries=True
        )

        fig.update_traces(showscale=False)

        engine = page.browser
        html = fig.to_html(include_plotlyjs='cdn')
        html = html.replace("<body>", "<body style='margin:0;padding:0'>")
        engine.setHtml(html)

        return page

    def page6(self):
        page = uic.loadUi('movies_page6.ui')
        networks = parseData.movie_studios()
        page.graph.setupUi(networks)

        return page

    def page7(self):
        page = uic.loadUi("movies_page7.ui")
        graph = parseData.movie_list_progress()
        page.graph.setupUi(graph)

        return page

    def page8(self):
        highest_rated, all_ratings = parseData.highest_rated_movies()

        ratings_quote = {10: 'TOTALLY NINJA!', 9: 'SUPERB', 8: 'GREAT', 7: 'GOOD', 6: 'FAIR', 5: 'MEH', 4: 'POOR',
                         3: 'BAD', 2: 'TERRIBLE', 1: 'WEAK SAUCE :('}

        page = uic.loadUi("movies_page8.ui")
        images = page.findChild(QtWidgets.QWidget, 'images')

        for id, poster in highest_rated.items():
            image = QtWidgets.QLabel()
            image.setStyleSheet('padding: 0; margin: 0; border: 0px;')
            image.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            image.setPixmap(QtGui.QPixmap(poster).scaled(114, 171, transformMode=QtCore.Qt.SmoothTransformation))
            images.layout().addWidget(image)

        grid = page.findChild(QtWidgets.QGridLayout, 'grid')

        total = sum(all_ratings.values())
        column = 0
        count = 0
        richtext = QtCore.QCoreApplication.translate

        for rating, value in all_ratings.items():
            perc = int((value / total) * 100)
            color = "#%06x" % random.randint(0, 0xFFFFFF)

            box = QtWidgets.QLabel(f"{perc}%")
            box.setAlignment(QtCore.Qt.AlignCenter)
            box_stylesheet = f""".QLabel {{background-color: {color}; color: {color}; font-size: 13px;}} .QLabel:hover {{color: white;}}"""
            box.setStyleSheet(box_stylesheet)

            line = QtWidgets.QFrame()
            line.setFrameShape(QtWidgets.QFrame.VLine | QtWidgets.QFrame.Sunken)
            line.setStyleSheet(f"background-color: {color}; color: {color};")
            label = QtWidgets.QLabel()
            label.setText(richtext("HOME",
                                   f"<html><head/><body><p style='margin-bottom:0; font-weight: bold;'>{rating} - {ratings_quote[rating]}</p><p style='margin: 0; padding-top: 0; font-size: 7pt; color: lightgrey;'>{value} SHOWS</p></body></html>"))
            label.setStyleSheet(f"padding-left: 5; background-color: black; color: white;")
            group = QtWidgets.QHBoxLayout()
            group.addWidget(line)
            group.addWidget(label)

            if count % 2 == 0:
                grid.addLayout(group, 0, column, 1, 2)
            else:
                grid.addLayout(group, 2, column, 1, 2)

            if perc in (0, 1, 2, 3):
                grid.addWidget(box, 1, column, 1, 4)
                column += (4 + 1)
            else:
                grid.addWidget(box, 1, column, 1, perc)
                column += (perc + 1)

            count += 1

        return page


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())