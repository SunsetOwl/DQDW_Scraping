import requests
import keys


class IGDBAPI:

    """This class handles fetching the ratings posted and collated by the IGDB."""

    def __init__(self):

        """Setup of the basic API access information"""

        self.url = "https://api.igdb.com/v4/games"
        self.id = keys.igdb_api_id()
        self.secret = keys.igdb_api_secret()

        # Generating the Bearer Token

        headers = {"client_id": self.id, "client_secret": self.secret, "grant_type": "client_credentials"}
        response = requests.post("https://id.twitch.tv/oauth2/token", headers)
        self.token = "Bearer " + response.json()["access_token"]

    def get_review_scores(self, games):

        """
        Given the dictionary games, which includes the game's IGDB ID, get the critic and user ratings
        :return:    An array of lists, containing the total and average ratings by users and critics respectively
                    [ [average user ratings game 1, game 2, ...], [total user ratings game 1, game 2, ...] etc.]
        """

        user_total_ratings = []
        user_avg_rating = []
        critic_total_ratings = []
        critic_avg_rating = []

        headers = {"Client-ID": self.id, "Authorization": self.token}
        fields = "id,name,aggregated_rating,aggregated_rating_count,rating,rating_count"

        for game in games.index:

            if games.loc[game]["IGDB ID"] != 0:

                data = "fields " + fields + "; where id = " + str(games.loc[game]["IGDB ID"]) + ";"

                response = requests.post(self.url, headers=headers, data=data)
                dataset = response.json()[0]
                if "rating" in dataset:
                    user_avg_rating.append(dataset["rating"]/10)
                else:
                    user_avg_rating.append(0)
                if "rating_count" in dataset:
                    user_total_ratings.append(dataset["rating_count"])
                else:
                    user_total_ratings.append(0)
                if "aggregated_rating" in dataset:
                    critic_avg_rating.append(dataset["aggregated_rating"]/10)
                else:
                    critic_avg_rating.append(0)
                if "aggregated_rating_count" in dataset:
                    critic_total_ratings.append(dataset["aggregated_rating_count"])
                else:
                    critic_total_ratings.append(0)

            else:
                user_avg_rating.append(0)
                user_total_ratings.append(0)
                critic_avg_rating.append(0)
                critic_total_ratings.append(0)

        return [user_avg_rating, user_total_ratings, critic_avg_rating, critic_total_ratings]




