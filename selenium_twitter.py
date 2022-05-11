import csv
import datetime
import time
import os.path

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.firefox.options import Options

from urllib.parse import quote


def create_webdriver_instance():
    options = Options()
    options.headless = True
    profile = webdriver.FirefoxProfile()
    profile.set_preference("intl.accept_languages", "en-US, en")
    driver = webdriver.Firefox(options=options, firefox_profile=profile)
    return driver


# def login_to_twitter(username, password, driver):
#     url = "https://twitter.com/login"

#     try:
#         driver.get(url)
#         xpath_username = '//input[@autocomplete="username"]'
#         xpath_password = '//input[@autocomplete="current-password"]'
#         xpath_email = '//input[@autocomplete="email"]'
#         WebDriverWait(driver, 10).until(
#             expected_conditions.presence_of_element_located((By.XPATH, xpath_username))
#         )

#         uid_input = driver.find_element(By.XPATH, xpath_username)
#         uid_input.send_keys(username)
#         uid_input.send_keys(Keys.RETURN)
#         WebDriverWait(driver, 10).until(
#             expected_conditions.presence_of_element_located((By.XPATH, xpath_password))
#         )
#     except exceptions.TimeoutException:
#         print("Timeout while waiting for Login screen")
#         return False

#     pwd_input = driver.find_element(
#         By.XPATH, '//input[@autocomplete="current-password"]'
#     )
#     pwd_input.send_keys(password)
#     pwd_input.send_keys(Keys.RETURN)

#     try:
#         WebDriverWait(driver, 10).until(
#             expected_conditions.presence_of_element_located((By.XPATH, xpath_email))
#         )
#         email_input = driver.find_element(By.XPATH, xpath_email)
#         email_input.send_keys("example@gmail.com")
#         email_input.send_keys(Keys.RETURN)
#     except:
#         pass
#     url = "https://twitter.com/home"
#     WebDriverWait(driver, 10).until(expected_conditions.url_to_be(url))
#     return True


# def find_search_input_and_enter_criteria(search_term, driver):
#     # xpath_search = '//*[(contains(@input,placeholder="Search Twitter"))]'
#     xpath_search = '//input[@enterkeyhint="search"]'
#     WebDriverWait(driver, 30).until(
#         expected_conditions.presence_of_element_located((By.XPATH, xpath_search))
#     )

#     search_input = driver.find_element(By.XPATH, xpath_search)
#     search_input.send_keys(search_term)
#     search_input.send_keys(Keys.RETURN)
#     return True


# def change_page_sort(tab_name, driver):
#     """Options for this program are `Latest` and `Top`"""
#     WebDriverWait(driver, 10).until(
#         expected_conditions.presence_of_element_located((By.LINK_TEXT, tab_name))
#     )
#     tab = driver.find_element(By.LINK_TEXT, tab_name)
#     tab.click()
#     xpath_tab_state = f'//a[contains(text(),"{tab_name}") and @aria-selected="true"]'


def generate_tweet_id(tweet):
    return "".join(tweet)


def scroll_down_page(
    driver, last_position, num_seconds_to_load=1.5, scroll_attempt=0, max_attempts=3
):
    """The function will try to scroll down the page and will check the current
    and last positions as an indicator. If the current and last positions are the same after `max_attempts`
    the assumption is that the end of the scroll region has been reached and the `end_of_scroll_region`
    flag will be returned as `True`"""
    end_of_scroll_region = False
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(num_seconds_to_load)
    try:
        curr_position = driver.execute_script("return window.pageYOffset;")
    except:
        curr_position = driver.execute_script("return window.pageYOffset;")
    if curr_position == last_position:
        if scroll_attempt < max_attempts:
            end_of_scroll_region = True
        else:
            scroll_down_page(last_position, curr_position, scroll_attempt + 1)
    last_position = curr_position
    return last_position, end_of_scroll_region


def save_tweet_data_to_csv(records, filepath, mode="a+"):
    header = [
        "User",
        "Handle",
        "PostDate",
        "TweetText",
        "ReplyCount",
        "RetweetCount",
        "LikeCount",
    ]
    with open(filepath, mode=mode, newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if mode == "w":
            writer.writerow(header)
        if records:
            writer.writerow(records)


def collect_all_tweets_from_current_view(driver, lookback_limit=25):
    """The page is continously loaded, so as you scroll down the number of tweets returned by this function will
    continue to grow. To limit the risk of 're-processing' the same tweet over and over again, you can set the
    `lookback_limit` to only process the last `x` number of tweets extracted from the page in each iteration.
    You may need to play around with this number to get something that works for you. I've set the default
    based on my computer settings and internet speed, etc..."""

    WebDriverWait(driver, 60).until(
        expected_conditions.presence_of_element_located(
            (By.XPATH, '//article[@data-testid="tweet"]')
        )
    )
    page_cards = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
    if len(page_cards) <= lookback_limit:
        return page_cards
    else:
        return page_cards[-lookback_limit:]


def extract_data_from_current_tweet_card(card):
    try:
        user = card.find_element(By.XPATH, ".//span").text
    except:
        user = ""
    try:
        handle = card.find_element(By.XPATH, './/span[contains(text(), "@")]').text
    except:
        handle = ""
    try:
        """
        If there is no post date here, there it is usually sponsored content, or some
        other form of content where post dates do not apply. You can set a default value
        for the postdate on Exception if you which to keep this record. By default I am
        excluding these.
        """
        postdate = card.find_element(By.XPATH, ".//time").get_attribute("datetime")
    except:
        return
    try:
        _comment = card.find_element(By.XPATH, ".//div[2]/div[2]/div[1]").text.replace(
            "\n", " "
        )
    except:
        _comment = ""
    try:
        _responding = card.find_element(
            By.XPATH, ".//div[2]/div[2]/div[2]"
        ).text.replace("\n", " ")
    except:
        _responding = ""
    tweet_text = _comment + _responding
    try:
        reply_count = card.find_element(By.XPATH, './/div[@data-testid="reply"]').text
    except:
        reply_count = ""
    try:
        retweet_count = card.find_element(
            By.XPATH, './/div[@data-testid="retweet"]'
        ).text
    except:
        retweet_count = ""
    try:
        like_count = card.find_element(By.XPATH, './/div[@data-testid="like"]').text
    except:
        like_count = ""

    tweet = (user, handle, postdate, tweet_text, reply_count, retweet_count, like_count)
    print(tweet)
    return tweet


def execute_code(driver, each_day, now, filepath, search_term, unique_tweets, step):
    last_position = None
    end_of_scroll_region = False
    since = now - datetime.timedelta(days=each_day)
    if each_day > step:
        with open(filepath, "r") as f:
            tweets = csv.DictReader(x.replace("\0", "") for x in f)
            last_tweet_date = datetime.datetime.strptime(
                [x for x in tweets][-1].get("PostDate")[:10], "%Y-%m-%d"
            )
            if (last_tweet_date - since).days > 90:
                return None
    end_of_scroll_region = False
    date_twitter = "%20until:{}%20since:{}".format(
        datetime.datetime.strftime(
            now - datetime.timedelta(days=each_day - step), "%Y-%m-%d"
        ),
        datetime.datetime.strftime(since, "%Y-%m-%d"),
    )
    # change_page_sort(page_sort, driver)
    url_to_go = "https://twitter.com/search?q={}&src=recent_search_click&f=live".format(
        quote(search_term) + date_twitter
    )
    print(url_to_go)
    driver.get(url_to_go)
    WebDriverWait(driver, 50).until(expected_conditions.url_to_be(url_to_go))
    while not end_of_scroll_region:
        try:
            cards = collect_all_tweets_from_current_view(driver)
        except:
            cards = []
        for card in cards:
            tweet = extract_data_from_current_tweet_card(card)
            if not tweet or not tweet[0] or not tweet[1]:
                print("no tweet")
                continue

            tweet_id = generate_tweet_id(tweet)
            if tweet_id not in unique_tweets:
                unique_tweets.add(tweet_id)
                save_tweet_data_to_csv(tweet, filepath,mode="a+")
        try:
            last_position, end_of_scroll_region = scroll_down_page(
                driver, last_position
            )
        except:
            time.sleep(5)
            last_position, end_of_scroll_region = scroll_down_page(
                driver, last_position
            )

        print(end_of_scroll_region, "end_of_scroll_region")


def main(search_term=None, file_name_=None, step=1):

    filepath = f"filesout/{file_name_}.csv"
    if not os.path.exists(filepath):
        save_tweet_data_to_csv(None, filepath,mode="w")  # create file for saving records
    unique_tweets = set()
    now = datetime.datetime.now()
    start_date = datetime.datetime.strptime("2006-3-21", "%Y-%m-%d")
    delta_days = (now - start_date).days
    for each_day in range(step, delta_days + step, step):
        wrong = False
        try:
            driver = create_webdriver_instance()
            time.sleep(20)
            execute_code(driver, each_day, now, filepath, search_term, unique_tweets, step=step,)
            driver.quit()
            time.sleep(10)
        except:
            wrong = True
        if wrong:
            driver = create_webdriver_instance()
            time.sleep(20)
            with open(filepath, "r") as f:
                tweets = csv.DictReader(x.replace("\0", "") for x in f)
                since = now - datetime.timedelta(days=each_day)
                print(tweets)
                tweets = [
                    x
                    for x in tweets
                    if datetime.datetime.strptime(x.get("PostDate")[:10], "%Y-%m-%d")
                    < since
                ]
                save_tweet_data_to_csv(None, filepath,mode="w")
                with open(filepath, mode="a+", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerows(tweets)
                execute_code(
                    driver,
                    each_day,
                    now,
                    filepath,
                    search_term,
                    unique_tweets,
                    step=step,
                )
            driver.quit()
            time.sleep(10)
