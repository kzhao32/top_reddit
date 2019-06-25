from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import time

def create_table(cursor):
    cursor.execute(
        "CREATE TABLE top_posts(" \
            "subreddit_post_hash text NOT NULL," \
            "top_rank smallint NOT NULL," \
            "time_top_rank_achieved timestamptz NOT NULL," \
            "subreddit text NOT NULL," \
            "title text NOT NULL," \
            "user text NOT NULL," \
            "creation_date timestamptz NOT NULL" \
        ");"
    )

def get_record(cursor, subreddit_post_host):
    print "TODO"
    #cursor.execute(" \
    #  SELECT COUNT \
    #  FROM top_posts \
    #  WHERE subreddit_post_host = \
    #  ")


def check_if_table_exists(cursor, table_name):
    cursor.execute( \
        "SELECT EXISTS (" \
            "SELECT 1 " \
            "FROM   information_schema.tables " \
            "WHERE  table_name = '" + table_name + "'" \
        ");" \
    )
    return cursor.fetchone()


def add_reddit_post(cursor, title, user, subreddit):
    print "TODO"


chrome_options = webdriver.ChromeOptions()
prefs = {"profile.default_content_setting_values.notifications" : 2}
chrome_options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(executable_path="./chromedriver", chrome_options=chrome_options)  # Tommy
#driver = webdriver.Firefox(executable_path="./geckodriver")  # Allen

actions = ActionChains(driver)
wait = WebDriverWait(driver, 5)  # Define max wait times.
MAX_NUM_RETRIES = 12

driver.get("https://www.reddit.com/")
wait.until(expected_conditions.visibility_of_element_located((By.ID, "SHORTCUT_FOCUSABLE_DIV")))

xpath_titles = "//a[@data-click-id='body']/h2"
xpath_posts = "//*[@id='SHORTCUT_FOCUSABLE_DIV']/div[2]/div/div/div/div[2]/div[4]/div[1]/div[1]/div"

posts = driver.find_elements_by_xpath(xpath_posts)
while len(posts) < 25:
    time.sleep(1)
    posts = driver.find_elements_by_xpath(xpath_posts)

def extract_and_print(webelement, xpath, key):
    webelements = webelement.find_elements_by_xpath(xpath)
    for webelement in webelements:
          if len(webelement.text) > 0:
              print(key + " = " + webelement.text)
              #if key == "timestamp":
              #       print(webelement.getAttribute("title"))

post_rank = 0
print(len(posts))
for post in posts:
    #driver.execute_script("arguments[0].scrollIntoView();", post)
    actions.move_to_element(post).perform()
    if len(post.find_elements_by_xpath(".//span[text()='promoted']")) > 0:
        continue # skip if is promoted or is an ad
    print("post_rank = " + str(post_rank))
    post_rank = post_rank + 1
    extract_and_print(post, ".//a[@data-click-id = 'body']/h2", "title")
    extract_and_print(post, ".//a[@data-click-id = 'subreddit']", "subreddit")
    extract_and_print(post, ".//a[contains(@href, '/user/')]", "user")
    timestamps = post.find_elements_by_xpath(".//a[@data-click-id = 'timestamp']")
    if len(timestamps) > 0:
        # FIXME there's an issue with not hovering over element if already on screen
        for n in range(MAX_NUM_RETRIES):
            try:
                #driver.execute_script("arguments[0].scrollIntoView();", timestamps[0])
                actions.move_to_element(timestamps[0]).perform()
                wait.until(expected_conditions.visibility_of_element_located((By.XPATH, "//div[@data-overflow='[object Object]']")))
                extract_and_print(driver, "//div[@data-overflow='[object Object]']", "timestamp")
                break
            except TimeoutException:
                pass
        

