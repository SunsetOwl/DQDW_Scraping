import pandas as pd

from steamcharts_scraper import SteamChartsScraper
from rawgapi import RAWGAPI
from igdbapi import IGDBAPI
from dataset_controller import DatasetController
import keys

steamcharts = SteamChartsScraper()
rawg = RAWGAPI()
igdb = IGDBAPI()

games = pd.read_csv("Sources/games.csv", header=0, index_col=0)
dc = DatasetController("gamedata.hdf5", games)

update_data = input("Do you want to update the data? Y/N \n")

if update_data in ["Y", "y", "yes"]:

    if keys.chrome_driver() == "" or keys.rawg_api_key() == "" or keys.igdb_api_secret() == "":

        print("You are missing information in the keys file. Please add your Chromium driver and API information")

    else:

        print("Updating, please wait.")

        igdb_results = igdb.get_review_scores(games)
        rawg_results = rawg.get_review_scores(games)
        steam_results = steamcharts.get_player_counts(games)

        dc.add_scrape("daily/user_avg_rating/igdb", igdb_results[0])
        dc.add_scrape("daily/user_votes/igdb", igdb_results[1])
        dc.add_scrape("daily/critic_avg_rating/igdb", igdb_results[2])
        dc.add_scrape("daily/critic_votes/igdb", igdb_results[3])

        dc.add_scrape("daily/user_votes/rawg", rawg_results[0])
        dc.add_scrape("daily/user_cat_rating/rawg", rawg_results[1])

        dc.add_scrape("daily/players/steam_charts", steam_results[0])
        dc.add_scrape("hourly/players/steam_charts", [steam_results[1], steam_results[2]])

else:
    print("Got it! Skipping the Update.")

print("Goodbye.")
