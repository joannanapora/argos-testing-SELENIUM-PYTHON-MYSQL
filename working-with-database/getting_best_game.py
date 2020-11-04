
import pymysql.cursors
import uuid


def finding_best_games():

    connection = pymysql.connect(host='localhost',
                                 user='sara',
                                 password='sarka',
                                 db='argos',
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            lowest_price = "SELECT * FROM argos.lowest_price"
            cursor.execute(lowest_price)
            customer_rating = "SELECT * FROM argos.customer_review"
            cursor.execute(customer_rating)
            best_games = "CREATE TABLE IF NOT EXISTS argos.best_games (id varchar(36), price varchar(10), title varchar(100))"
            cursor.execute(best_games)
            sorting_games = "SELECT * FROM argos.customer_review INNER JOIN argos.lowest_price ON argos.customer_review.title = argos.lowest_price.title"
            cursor.execute(sorting_games)
            sorting_games = cursor.fetchall()

            for i, game in enumerate(sorting_games):
                print(game)
                the_best_of_the_best = "INSERT INTO argos.best_games (id, price, title) VALUES (%s, %s, %s)"
                id = uuid.uuid4()
                cursor.execute(
                    the_best_of_the_best, (str(id), game["price"], game["title"]))
                connection.commit()

    finally:
        connection.close()


if __name__ == "__main__":

    finding_best_games()
