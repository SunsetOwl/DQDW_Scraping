import requests
import keys


class RAWGAPI:

    """This class handles fetching the ratings posted and collated by RAWG."""

    def __init__(self):

        """Setup of the basic API access information"""

        self.url = "https://api.rawg.io/api/games/"
        self.key = keys.rawg_api_key()

    def get_review_scores(self, games):

        """
        Given the dictionary games, which includes the game's RAWG link, get the user ratings
        :return:    An array of lists, containing the total and average ratings by users
        """

        total_ratings = []
        rating_counts = []

        for game in games.index:

            if games.loc[game]["RAWG Url"] != "-":

                request_result = requests.get(url=self.url + games.loc[game]["RAWG Url"], params={"key": self.key})
                ratings = request_result.json()["ratings"]
                rating_count = [0, 0, 0, 0]

                # RAWG ratings are split into "Exceptional" (5), "Recommended" (4), "Meh" (3) and "Skip" (1)
                for category in ratings:
                    match category["id"]:
                        case 1:
                            rating_count[0] = category["count"]
                        case 3:
                            rating_count[1] = category["count"]
                        case 4:
                            rating_count[2] = category["count"]
                        case 5:
                            rating_count[3] = category["count"]

                ratings_string = " ".join([str(count) for count in rating_count])

                total_ratings.append(request_result.json()["reviews_count"])
                rating_counts.append(ratings_string)

            else:
                total_ratings.append(0)
                rating_counts.append([])

        return [total_ratings, rating_counts]
