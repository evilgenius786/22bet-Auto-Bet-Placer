import json
import os
import time
import traceback

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

t = 1
timeout = 5

debug = test = os.path.isfile('debug')

headless = False
images = True
max = True
email = "gcosta@sokkerpro.com"
passwd = "bangabc123"
incognito = False
placed = []


def main():
    logo()
    driver = getChromeDriver()
    if test:
        bet = 1
        match = driver.current_url
        clicktov(driver, getElement(driver, '//div[normalize-space()="Total"]/../div[2]/div[1]'), "1", bet)
        placebet(driver, bet, match)
        clicktov(driver, getElement(driver, '//div[normalize-space()="Total"]/../div[2]/div[3]'), "3", bet)
        placebet(driver, bet, match)
        input("Done")
    driver.get('https://22bet.com/live/Football/')
    print("Score is always 0:0")
    mintime = input("Enter min time:").split(":")
    maxtime = input("Enter max time:").split(":")
    minda = int(input("Enter minimum dangerous attacks:"))
    tov = float(input("Enter minimum value for Total Over: "))
    bet = int(input("Enter value to place a bet on the Total Over market: "))
    if "curLoginForm" in driver.page_source and not test:
        print("Logging in...")
        click(driver, '//*[@id="curLoginForm"]')
        sendkeys(driver, '//*[@placeholder="ID or Email"]', email)
        sendkeys(driver, '//*[@placeholder="Password"]', passwd)
        click(driver, '//*[@for="remember_user"]')
        click(driver, '//a[contains(text(),"Log in")]')
        input("Press enter after successfull login...")
    else:
        print("Already logged in!")
    while True:
        leagues = [league.get_attribute('href') for league in getElements(driver, '//li/a[@class="link"]')]
        print("Total leagues", len(leagues))
        for league in leagues:
            try:
                print("League", league)
                driver.get(league)
                time.sleep(1)
                matches = [match.get_attribute('href') for match in
                           getElements(driver, '//ul[@class="event_menu"]/li/a')]
                print("Matches", len(matches))
                for match in matches:
                    try:
                        print(match)
                        if not test:
                            driver.get(match)
                        time.sleep(1)
                        # getElement(driver, '//*[@id="game-filters"]/option[1]')
                        if len(driver.find_elements_by_xpath('//option[normalize-space()="1 Half Corners"]')) == 0:
                            print("No 1 Half Corners available")
                        elif len(driver.find_elements_by_xpath('//div[normalize-space()="Total"]')) == 0:
                            print("Total not available.")
                        elif len(driver.find_elements_by_xpath('//div[contains(text(),"Dangerous attacks")]')) == 0:
                            print("Dangerous Attack not available.")
                        else:
                            score = getElement(driver, '//div[@class="g-scoreboard-item__score"]').text
                            if score != "0 : 0":
                                print(f"Expected score: 0 : 0 | found {score}")
                            else:
                                Select(getElement(driver, '//*[@id="game-filters"]')).select_by_visible_text(
                                    "1 Half Corners")
                                time.sleep(2)
                                tov1 = getElement(driver, '//div[normalize-space()="Total"]/../div[2]/div[1]')
                                at = getElement(driver, '//div[contains(text(),"Dangerous attacks")]/../../div[2]')
                                driver.execute_script("arguments[0].scrollIntoView();", at)
                                attacks = at.text.split()
                                matchtime = getElement(driver, '//div[@class="g-scoreboard-top__count"]').text.split(
                                    ":")
                                print("======================================")
                                print("Dangerous Attacks", attacks)
                                print("Time", matchtime)
                                print("Score", score)
                                print(tov1.text.split('\n'))
                                tov2 = None
                                try:
                                    tov2 = getElement(driver, '//div[normalize-space()="Total"]/../div[2]/div[3]')
                                    print(tov2.text.split('\n'))
                                except:
                                    pass
                                print("======================================")
                                time.sleep(1)
                                if int(attacks[0]) < minda and int(attacks[1]) < minda:
                                    print("Dangerous attacks not enough.")
                                elif int(matchtime[0]) < int(mintime[0]) or (
                                        int(matchtime[0]) == int(mintime[0]) and int(matchtime[1]) < int(mintime[1])):
                                    print("Time less than minimum time.")
                                elif int(matchtime[0]) > int(maxtime[0]) or (
                                        int(matchtime[0]) == int(maxtime[0]) and int(matchtime[1]) > int(maxtime[1])):
                                    print("Time more than maximum time.")
                                elif float(tov1.text.split('\n')[1]) < tov and (
                                        tov2 is None or float(tov2.text.split('\n')[1]) < tov):
                                    print("Total Over not satisfied")
                                elif match in placed:
                                    print("Already placed bet on", match)
                                else:
                                    print("All requirements satisfied, placing bet!")
                                    loop(driver, bet, tov, 0)
                                print("_____________________________________")
                    except:
                        print("Error on match", match)
                        traceback.print_exc()
            except:
                print("Error on league", league)
                traceback.print_exc()
        driver.get('https://22bet.com/live/Football/')


def loop(driver, bet, tov, i):
    if i > 4:
        print("Enable to place bet", driver.current_url)
        return
    match = driver.current_url
    tov1 = getElement(driver, '//div[normalize-space()="Total"]/../div[2]/div[1]')
    tov2 = None
    try:
        tov2 = getElement(driver, '//div[normalize-space()="Total"]/../div[2]/div[3]')
        print(tov2.text.split('\n'))
    except:
        pass
    try:

        if float(tov1.text.split('\n')[1]) > tov:
            clicktov(driver, tov1, "1", bet)
            placebet(driver, bet, match)
        if tov2 is not None and float(tov2.text.split('\n')[1]) > tov:
            clicktov(driver, tov2, "3", bet)
            placebet(driver, bet, match)
    except:
        print("Error placing bet", match)
        traceback.print_exc()
        driver.refresh()
        time.sleep(1)
        loop(driver, bet, tov, i + 1)


def clicktov(driver, tov0, div, bet):
    for i in range(5):
        while "clearAllBetsBlock" in driver.page_source:
            try:
                driver.find_element_by_xpath('//*[@id="clearAllBetsBlock"]').click()
            except:
                pass
        click(driver, f'//div[normalize-space()="Total"]/../div[2]/div[{div}]', True)
        if getElement(driver,
                      f'//div[normalize-space()="Total"]/../div[2]/div[{div}]').get_attribute(
            "class") == "c-bets__active":
            break
    x = tov0.text.replace('\n', ' = ')
    print(f"Placing bet on {x} for {bet}")


def placebet(driver, bet, match):
    for i in range(5):
        try:
            if getElement(driver,
                          '//span[@class="multiselect__single"]').text == "Change":
                click(driver, '//span[@class="multiselect__single"]')
                click(driver, '//span[text()="Accept any change"]')
                print("Changing to 'Accept any change'.")
            for i in range(5):
                sendkeys(driver, '//*[@id="bet_input"]', "", True)
                sendkeys(driver, '//*[@id="bet_input"]', bet, False)
                time.sleep(1)
                if getElement(driver, '//*[@id="bet_input"]').get_attribute('value') == str(bet):
                    break
                time.sleep(1)
            driver.execute_script("arguments[0].scrollIntoView();",
                                  driver.find_element_by_xpath('//*[@id="goPutBetButton"]'))
            click(driver, '//*[@id="goPutBetButton"]', True)
            print("Bet placed on", match)
            time.sleep(1)
            while "alert-sob" not in driver.page_source:
                time.sleep(1)
            time.sleep(1)
            print(getElement(driver, '//div[@class="alert-sob"]').text.split("\n"))
            placed.append(match)
            click(driver, '//button[@class="alert_link"]')
            break
        except:
            try:
                click(driver, '//button[@type="button" and text()="OK"]')
            except:
                pass


def click(driver, xpath, js=False):
    driver.execute_script("arguments[0].scrollIntoView();", getElement(driver, xpath))
    if js:
        driver.execute_script("arguments[0].click();", getElement(driver, xpath))
    else:
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath))).click()


def getElement(driver, xpath):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))


def getElements(driver, xpath):
    return WebDriverWait(driver, timeout).until(EC.presence_of_all_elements_located((By.XPATH, xpath)))


def sendkeys(driver, xpath, keys, js=False):
    if js:
        driver.execute_script(f"arguments[0].value='{keys}';", getElement(driver, xpath))
    else:
        getElement(driver, xpath).send_keys(keys)


def getChromeDriver(proxy=None):
    options = webdriver.ChromeOptions()
    if debug:
        # print("Connecting existing Chrome for debugging...")
        options.debugger_address = "127.0.0.1:9222"
    else:
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-blink-features")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument('--user-data-dir=C:\\Selenium\\ChromeProfile')
    if not images:
        # print("Turning off images to save bandwidth")
        options.add_argument("--blink-settings=imagesEnabled=false")
    if headless:
        # print("Going headless")
        options.add_argument("--headless")
        options.add_argument("--window-size=1920x1080")
    if max:
        # print("Maximizing Chrome ")
        options.add_argument("--start-maximized")
    if proxy:
        # print(f"Adding proxy: {proxy}")
        options.add_argument(f"--proxy-server={proxy}")
    if incognito:
        # print("Going incognito")
        options.add_argument("--incognito")
    return webdriver.Chrome(options=options)


def getFirefoxDriver():
    options = webdriver.FirefoxOptions()
    if not images:
        # print("Turning off images to save bandwidth")
        options.set_preference("permissions.default.image", 2)
    if incognito:
        # print("Enabling incognito mode")
        options.set_preference("browser.privatebrowsing.autostart", True)
    if headless:
        # print("Hiding Firefox")
        options.add_argument("--headless")
        options.add_argument("--window-size=1920x1080")
    return webdriver.Firefox(options)


def logo():
    os.system('color 0a')
    print(r"""
           ___  ___   __         __ 
          |__ \|__ \ / /_  ___  / /_
          __/ /__/ // __ \/ _ \/ __/
         / __// __// /Q_/ /  __/ /_  
        /____/____/_.___/\___/\__/  
==============================================
    22bet.com auto bet placing script by:
        github.com/evilgenius786
==============================================
[+] Browser based
[+] Automatic
______________________________________________
""")


def sm():
    api_key = "aFiadwy26Hx2v9Kxr2jKJ6RWbJDJmFYwZjuje95DAERwtWs4vPO1Bx8FmK6u"
    sportmonks = "https://soccer.sportmonks.com/api/v2.0"
    fixture = json.loads(
        requests.get(f'{sportmonks}/odds/inplay/fixture/{18293037}?api_token={api_key}&bookmakers=25679340').text)
    input(json.dumps(fixture, indent=4))

    livescores = json.loads(requests.get(f'{sportmonks}/livescores/now?api_token={api_key}&bookmakers=25679340').text)
    with open("livescores.json", 'w') as lfile:
        json.dump(livescores, lfile, indent=4)
    for data in livescores['data']:
        print(json.dumps(data, indent=4))
        break


if __name__ == "__main__":
    try:
        main()
    except:
        traceback.print_exc()
