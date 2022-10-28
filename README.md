# Traktstats
Trakt [all-time-stats](https://blog.trakt.tv/all-time-year-in-review-f6f931e4461d) without Trakt VIP

# Prerequisite
* Python3
* [Trakt Client ID](https://trakt.tv/oauth/applications)
* [TMDB API key](https://www.themoviedb.org/settings/api)
* Full export of trakt data using [traktexport](https://github.com/seanbreckenridge/traktexport)

# Usage
```sh
poetry install # one time
TMDB_API_KEY="value-here" TRAKT_API_KEY="value-here" python ui.py
```

# Note
* Program UI is only optimized for 1360x768 resolution
* As i made it only for personal use, the code is messy and has no comments.
