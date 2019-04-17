# Standard Library Imports
import random
import time
import json

# Third Party Imports
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# User inputs
chrome_path = r"your\path\to\chromedriver.exe"
home_user="yourusernamehere"



#####################################################################################





# Store credentials (as dictionary) in config.json, if you want
try:
    with open("config.json") as f:
        config_json = json.load(f)
except FileNotFoundError:
    config_json = {}
chrome_path = config_json.get('chrome_path', chrome_path)
assert chrome_path != r"your\path\to\chromedriver.exe", "You need to set the path to your Chrome Driver executable!"
home_user = config_json.get('home_user', home_user)
assert home_user != "yourusernamehere", "You need to set your username!"
env = config_json.get('env', 'prod')


driver = webdriver.Chrome(chrome_path)
driver.get('https://www.depop.com/')
time.sleep(3)
if env == 'prod':
    # If in production we should login
    [elm.click() for elm in driver.find_elements_by_xpath("""//span[text()="Login"]""") if elm.text=="Login"]      #Clicks login button
    input("Type in login details, then press enter, then press enter to continue running script")
    mode = input("select mode (following, unfollowing):")
else:
    mode = 'following'


# Ascertain statistics about the home_user
driver.get('https://www.depop.com/'+home_user)
time.sleep(3)
prof_following_elm = driver.find_element_by_xpath("""//span[contains(text(),'Following')]""").find_element_by_xpath("..")
prof_following_num = int(prof_following_elm.text.replace(' Following',''))
prof_follower_elm = driver.find_element_by_xpath("""//span[contains(text(),'Followers')]""").find_element_by_xpath("..")
prof_follower_num = int(prof_follower_elm.text.replace(' Followers',''))
print("You are following {} user(s) and have {} follower(s).".format(prof_following_num, prof_follower_num))

# Enter following mode
if mode=="following":
    total_users_followed = 0
    # TODO: Try to just start following from either the users follower list or following list
    # Just enter in a username for now
    if env == 'prod':
        username = input("First username to use:")
    else:
        # I'm lazy
        username = 'gsvwear'
    # Navigate to user
    driver.get('https://www.depop.com/' + username)
    user_follower_elm = driver.find_element_by_xpath("""//span[contains(text(),'Followers')]""")\
        .find_element_by_xpath("..")
    user_follower_num = int(user_follower_elm.text.replace(' Followers', ''))

    # You're probably better off just stopping after a certain amount of time
    # Rather than a particular number of users
    break_time = 30

    # Click on the users follower list
    user_follower_elm.click()
    time.sleep(8)



    # Start following
    scroll_elm = driver.find_element_by_tag_name('html')
    new_start_time = time.time()
    _num_followed = 0
    _followed_users = []
    while time.time() - new_start_time < 30:
        # Click on the follower name to bring the follower list into scope
        driver.find_elements_by_xpath("""//p[contains(text(),'@')]""")[1:][0].click()
        _user_names = [u.text.replace('@', '') for u in driver.find_elements_by_xpath("""//p[contains(text(),'@')]""")]

        # Don't try to follow users if we already followed them
        _user_names = [u for u in _user_names if u not in _followed_users]
        _user_elms = [e for e in driver.find_elements_by_xpath("""//span[contains(text(),'Follow')]""")[1:] if e.text == 'Follow']
        _user_elms = _user_elms[_num_followed:]
        for u, e in zip(_user_names, _user_elms):
            print("Trying to follow: {}".format(u))
            e.click()
            print("Successfully followed: {}".format(u))
            if env == 'dev':
                # Close out of the both that comes up because I don't have an account
                time.sleep(2)
                # TODO: Fill bare exceptions
                try:
                    driver.find_element_by_xpath("""//*[@id="mount"]/div/div/div[7]/div[2]/*""").click()
                except:
                    try:
                        driver.find_element_by_xpath("""/html/body/div[4]/div/div[2]/div/div/svg/path""").click()
                    except:
                        pass
                time.sleep(2)
                # Refocus the scrolling
            try:
                driver.find_elements_by_xpath("""//p[contains(text(),'@')]""")[1:][0].click()
            except:
                print("Could not refocus scrolling element")
            scroll_elm.send_keys(Keys.END)









if mode=="unfollowing":
    prof_following_elm.click()
    time.sleep(3)
    scroll_elm = driver.find_element_by_tag_name('html')
    sauce=driver.page_source
    sauce=sauce.split()
    sauce=[i for i in sauce if "Following" in i and "span" in i][-1]
    data_word=sauce.split("=")[0]
    users_unfollowed=0
    reset_switch=0
    while users_unfollowed<prof_following_num:
        scroll_elm.send_keys(Keys.END)
        for user in driver.find_elements_by_css_selector("["+data_word+"='']"):
            try:
                user.click()
                users_unfollowed=users_unfollowed+1
                reset_switch=reset_switch+1
            except:
                pass
        if reset_switch>300:
            driver.refresh()
            prof_following_elm = driver.find_element_by_xpath("""//span[contains(text(),'Following')]""").find_element_by_xpath("..")
            prof_following_num = int(prof_following_elm.text.replace(' Following',''))
            prof_following_elm.click()
            time.sleep(3)
            users_unfollowed=0
            reset_switch=0
            scroll_elm = driver.find_element_by_tag_name('html')
    print("Done unfollowing.")


if env == 'dev':
    driver.close()
        
