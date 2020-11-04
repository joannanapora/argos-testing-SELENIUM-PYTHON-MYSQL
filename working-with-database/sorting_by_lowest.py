from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import pymysql.cursors
import unittest
from selenium.webdriver.common.action_chains import ActionChains
import time
import sys
import uuid

# export PATH=$PATH:/Users/porczi/Desktop/drivers

# searching Nintendo Switch games from 40-60 pounds using price filters "25-50" and "50-100"
# connecting to mysql and create tables "sorted_by_lowest" and "sorted_by_customer_rating"
# basing on previous table, create new table "best_to_buy" with game titles that appear in both


class argos(unittest.TestCase):

    def sorting_by_lowest_price(self):
        driver = self.driver
        wait = self.wait

        sort_by = driver.find_element_by_xpath(
            "//select[@id='sort-select']")
        sort_by.click()
        low_to_high = driver.find_element_by_xpath(
            "//option[contains(text(),'Price: Low - High')]")
        low_to_high.click()
        games = driver.find_elements_by_xpath(
            "//div[@class='ProductCardstyles__TextContainer-sc-1fgptbz-6 faVtmd']")

        games_details = []
        i = 2
        navi = driver.find_elements_by_xpath(
            "//nav[@class ='Paginationstyles__Pagination-sc-1hvuf20-0 cNMqiM styles__FindabilityPagination-sc-1ajl292-0 QoYUu xs-row']/a")

        last_page = navi[-2].text

        while True:
            for game in games:
                price = game.find_element_by_xpath(
                    ".//div[@class='ProductCardstyles__PriceText-sc-1fgptbz-14 iSKBrf']").text
                price = price.replace("£", "")

                if float(price) >= 40 and float(price) <= 60:
                    title = game.find_element_by_xpath(
                        ".//a[@class ='ProductCardstyles__Title-sc-1fgptbz-12 jdEaFQ']").text
                    games_details.append({"price": price, "title": title})

            hover_next_page = ActionChains(
                driver).move_to_element(navi[0])
            hover_next_page.perform()

            if i > int(last_page):
                break

            navi[-1].click()

            wait.until(EC.invisibility_of_element(
                (By.XPATH, "//body[1]/main[1]/div[1]/div[3]/div[1]/div[7]/div[1]/div[5]/div[4]/div[5]/div[1]/svg[1]/rect[1]")))
            games = driver.find_elements_by_xpath(
                "//div[@class='ProductCardstyles__TextContainer-sc-1fgptbz-6 faVtmd']")

            i = i+1
        return games_details

    def setUp(self):
        self.driver = Chrome()
        self.wait = WebDriverWait(self.driver, 15)

    def test_argos(self):
        driver = self.driver
        wait = self.wait

        driver.get("https://argos.co.uk")
        self.assertIn("Argos", driver.title)
        driver.maximize_window()

        # closing cookies
        cookies = driver.find_element_by_xpath(
            "//div[@class='consent_prompt_footer']/button")
        cookies.click()
        # going to nintendo games through main manu
        shop = driver.find_element_by_xpath("//div[@class='_1KJZb']/li/a")
        hover_shop = ActionChains(driver).move_to_element(shop)
        hover_shop.perform()
        wait.until(EC.visibility_of_all_elements_located(
            (By.XPATH, "//li[@class='mega-menu-column']")))

        technology = driver.find_element_by_xpath(
            "//header/div[2]/div[1]/nav[1]/ul[1]/ul[1]/li[1]/ul[1]/ul[1]/li[2]/a[1]")
        hover_technology = ActionChains(driver).move_to_element(technology)
        hover_technology.perform()

        nintendo_switch = driver.find_element_by_xpath(
            "//a[contains(text(),'Switch Games')]")
        nintendo_switch.click()

        # assertion on title
        search_title = driver.find_element_by_xpath(
            "//div[@class='styles__SearchTitle-sc-1haccah-0 kAkKBD']/h1").text
        assert search_title == 'Nintendo Switch games'

        # setting price filters
        price_25_50 = driver.find_element_by_xpath(
            "//body/main[@id='app']/div[1]/div[3]/div[1]/div[7]/div[1]/div[3]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/label[5]/div[1]/div[1]/*[1]")
        price_25_50.click()

        wait.until(EC.text_to_be_present_in_element(
            (By.XPATH, "//body/main[@id='app']/div[1]/div[3]/div[1]/div[7]/div[1]/div[3]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/ul[1]/li[1]/span[1]"), "£25 - £50"))

        show_more = driver.find_element_by_xpath(
            "// body/main[@id='app']/div[1]/div[3]/div[1]/div[7]/div[1]/div[3]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[3]/div[1]/button[3]")
        show_more.click()

        price_50_100 = driver.find_element_by_xpath(
            "//body/main[@id='app']/div[1]/div[3]/div[1]/div[7]/div[1]/div[3]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[3]/div[1]/div[1]/div[1]/div[2]/div[1]/label[1]/div[1]/div[1]/*[1]")
        price_50_100.click()

        wait.until(EC.text_to_be_present_in_element(
            (By.XPATH, "//body/main[@id='app']/div[1]/div[3]/div[1]/div[7]/div[1]/div[3]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/ul[1]/li[1]/span[1]"), "£50 - £100"))

        # calling function to sort by lowest price
        games_details = self.sorting_by_lowest_price()

        # connecting to database and send data
        connection = pymysql.connect(host='localhost',
                                     user='sara',
                                     password='sarka',
                                     db='argos',
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)

        try:
            with connection.cursor() as cursor:
                for i in games_details:
                    sql = "CREATE TABLE IF NOT EXISTS argos.lowest_price (id varchar(36), price varchar(100), title varchar(100))"
                    cursor.execute(sql)
                    # Create a new record
                    sql = "INSERT INTO argos.lowest_price (id, price, title) VALUES (%s, %s, %s)"
                    id = uuid.uuid4()
                    cursor.execute(
                        sql, (str(id), i["price"], i["title"]))
                    connection.commit()
        finally:
            connection.close()

    def tear_down(self):
        self.driver.quit()


if __name__ == "__main__":
    unittest.main()
