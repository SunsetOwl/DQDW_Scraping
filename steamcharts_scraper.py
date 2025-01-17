from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import pandas as pd
from datetime import datetime
import time

import keys


class SteamChartsScraper:

    """This class handles scraping the Steam Charts Website using selenium for player counts."""

    def __init__(self):

        """Setup of the basic Scraper Information"""

        self.driver_path = keys.chrome_driver()
        self.user_agent = keys.steamcharts_agent()
        self.website_url = "https://steamcharts.com/"

    def _setup_driver(self):

        """
        Setup of the selenium webdriver to collect the website contents via the Chrome browser
        :return: driver - the selenium webdriver
        """

        service = Service(executable_path=self.driver_path)
        options = webdriver.ChromeOptions()
        options.add_argument("--user-agent=" + self.user_agent)
        driver = webdriver.Chrome(service=service, options=options)

        # Clear the Cookie popup to be able to access the tooltips of the player graph later on

        driver.get(self.website_url)

        # Wait for the Privacy popup window
        # If the code breaks, check whether the frame has been renamed

        WebDriverWait(driver, 5).until(
            expected_conditions.frame_to_be_available_and_switch_to_it(
                (By.XPATH, "//iframe[@id='sp_message_iframe_1140461']")
            )
        )

        webdriver.ActionChains(driver).click(driver.find_element(By.XPATH, '//button[@title="Accept"]')).perform()

        # Wait to make sure the popup has closed

        time.sleep(2)

        # Return to the main page

        driver.switch_to.default_content()

        return driver

    def get_player_counts(self, games):

        """
        Given the dictionary games, which includes the game's ID on Steam, get the number of players
        :return: games - Lists containing the number of players as well as the all-time peaks
        """

        driver = self._setup_driver()
        all_time_peaks = []
        timestamps = []
        player_counts = []
        requested = []

        for game in games.index:
            if games.loc[game]["Steam AppID"] != 0:

                url = self.website_url + "app/" + str(games.loc[game]["Steam AppID"])
                driver.get(url)

                requested.append(datetime.now())

                # Get the simple data immediately available from the header
                counts = driver.find_elements(By.CLASS_NAME, "num")
                all_time_peaks.append(int(str.replace(counts[2].text, ",", "")))

                webdriver.ActionChains(driver).click(driver.find_element(By.CLASS_NAME, "highcharts-button")).perform()

                webdriver.ActionChains(driver).move_to_element_with_offset(
                    driver.find_element(By.CLASS_NAME, "highcharts-container"), -360, 0).perform()

                hourly_counts = []
                times = []

                for i in range(0, 55):
                    record = driver.find_elements(By.CLASS_NAME, "highcharts-tooltip")[0].text
                    if record != "":
                        date_text = record.split("●")[0]
                        date_only_text = date_text.split(",")[1] + "-" + date_text.split(",")[2]
                        date = pd.to_datetime(date_only_text, format=" %b %d- %H:%M")
                        date = date.replace(
                            year=datetime.now().year)  # Doesn't take New Years into account as it ran within one year

                        if date not in times:
                            times.append(date)

                            players_text = record.split(":")[-1]
                            hourly_counts.append(int(str.strip(str.replace(players_text, ",", ""))))

                    webdriver.ActionChains(driver).move_by_offset(14, 0).perform()

                timestamps.append(times)
                player_counts.append(hourly_counts)

            else:
                all_time_peaks.append(0)
                timestamps.append([])
                player_counts.append([])
                requested.append(datetime.now())

        driver.quit()

        return [all_time_peaks, timestamps, player_counts, requested]
