# Standard Library Imports
import random
import time
import json

# Third Party Imports
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# Local Imports
from depop_exceptions import *

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


# driver should be global/reused
driver = webdriver.Chrome(chrome_path)



class Follower(object):
    BASE_URL = 'https://www.depop.com/'
    def __init__(self, driver, home_user="", env='prod'):
        print("Starting Depop Follower...")
        self.driver = driver
        self.total_users_followed = 0
        self.mode = None
        self.env = env
        self.home_user = home_user
        self.home_user_num_followers = 0
        self.home_user_num_following = 0
        self.on_user_page = False
        self.on_follower_list = False
        self.on_following_list = False
        self.home_user_logged_in = False
        if self.env == 'prod':
            self.current_username = input("First username to use:")
        else:
            # I'm lazy
            self.current_username = 'gsvwear'
        self.current_username_num_followers = 0
        self.current_username_num_following = 0
        self.followed_users = []
        self.window_size = None

    def set_on_attr(self, attr_to_set):
        self.on_user_page = False
        self.on_follower_list = False
        self.on_following_list = False
        setattr(self, attr_to_set, True)

    def find_element(self, callable, arg, error=""):
        if not error:
            error = "Failed to find an element with string arg {}".format(arg)
        try:
            ret = callable(arg)
        except Exception as e:
            print(error)
            raise e
        return ret

    def find_elements(self, callable, arg, error=""):
        if not error:
            error = "Failed to find elements with string arg {}".format(arg)
        try:
            ret = callable(arg)
        except Exception as e:
            print(error)
            raise FindingElementError(error)
        return ret

    def click_elm(self, elm, error=""):
        if not error:
            error = "Failed to click element with text {}".format(elm.text)
        try:
            elm.click()
        except Exception as e:
            print(error)
            raise e

    def nav_to_user(self, username=None):
        if not username:
            username = self.current_username
        self.driver.get(self.BASE_URL + username)
        self.set_on_attr('on_user_page')

    def nav_to_mainpage(self):
        # Make the driver and navigate to the depop main page.
        self.driver.get(self.BASE_URL)
        time.sleep(3)
        if env == 'prod':
            # If in production we should login
            elms = self.find_elements(self.driver.find_elements_by_xpath, """//span[text()="Login"]""",
                                      "Failed to find login elements")
            for elm in elms:
                if elm.text == "Login":
                    self.click_elm(elm, error="Failed to click login button")
            input("Type in login details, then press enter, then press enter to continue running script")
            self.home_user_logged_in = True
            self.mode = input("select mode (following, unfollowing):")
        else:
            self.mode = 'following'
        assert self.mode == 'following' or self.mode == 'unfollowing', "Unrecognized mode."

    def _get_following_elm(self):
        following_elm_child = self.find_element(self.driver.find_element_by_xpath,
                                           """//span[contains(text(),'Following')]""",
                                           error="Couldn't find Following element child")
        # Have to do this :shrug:
        # TODO: Fix. You should enable method on obj that isn't driver
        try:
            following_elm_parent = following_elm_child.find_element_by_xpath("..")
        except Exception as e:
            print("Failed to find following element parent")
            raise e
        return following_elm_parent

    def _get_follower_elm(self):
        follower_elm_child = self.find_element(self.driver.find_element_by_xpath,
                                           """//span[contains(text(),'Followers')]""",
                                           error="Couldn't find Follower element child")
        # Have to do this :shrug:
        # TODO: Fix. You should enable method on obj that isn't driver
        try:
            follower_elm_parent = follower_elm_child.find_element_by_xpath("..")
        except Exception as e:
            print("Failed to find follower element parent")
            raise e
        return follower_elm_parent

    def print_elm_attrs(self, elm):
        print("Location: ", elm.location,
              "Size: ", elm.size,
              "Text: ", elm.text,
              "Is selected:", elm.is_selected(),
              "Is enabled:", elm.is_enabled())

    def get_user_stats(self, username=None):
        if not username:
            username = self.current_username
        self.nav_to_user(username)
        if not self.on_user_page:
            raise ValueError("You're trying to ascertain user stats, but you aren't on the user page")
        print("Getting stats for {}".format(username))

        following_elm_parent = self._get_following_elm()
        self.current_username_num_following = int(following_elm_parent.text.replace(' Following', ''))
        follower_elm_parent = self._get_follower_elm()
        self.current_username_num_followers = int(follower_elm_parent.text.replace(' Followers', ''))

        if self.current_username == self.home_user:
            self.home_user_num_following = self.current_username_num_following
            self.home_user_num_followers = self.current_username_num_followers
            print("{} is following {} user(s) "
                  "and have {} follower(s).".format(username,
                                                    self.home_user_num_following,
                                                    self.home_user_num_followers))

    def click_on_follower_list(self):
        self.click_elm(self._get_follower_elm())
        elms = []
        while not elms:
            elms = self.find_elements(driver.find_elements_by_xpath, """//p[contains(text(),'@')]""")[1:]
            time.sleep(1)
        print("Follower list loaded successfully")

    def click_on_following_list(self):
        self.click_elm(self._get_following_elm())

    def follow_from_list(self, max_num=50):
        max_to_follow = min(max_num, self.current_username_num_followers)
        i = 0
        leading_ind = 1


        name_elms = self.find_elements(driver.find_elements_by_xpath, """//p[contains(text(),'@')]""",
                                       "Could not get name elms")[leading_ind:]
        # Rescope the follower list
        self.click_elm(name_elms[-1])
        follow_btns_elms = self.find_elements(driver.find_elements_by_xpath, """//span[contains(text(),'Follow')]""",
                                              "Could not get follow button elms")[leading_ind:]
        follow_btns_elms = [e for e in follow_btns_elms if e.text == "Follow"]
        unames = [e.text.replace('@', '') for e in name_elms]




        while i < max_to_follow:
            for uname, fol_btn in zip(unames, follow_btns_elms):
                if uname not in self.followed_users:
                    print("Attempting to follow {}".format(uname))
                    print("Attempting click on follower button")
                    try:
                        self.click_elm(fol_btn)
                    except Exception as e:
                        print(str(e))
                        print("Trying to click elm anyways")
                        try:
                            action = webdriver.common.action_chains.ActionChains(self.driver)
                            action.move_to_element_with_offset(fol_btn, 100, 100).click().perform()
                        except Exception as e:
                            raise e
                        time.sleep(100)
                    # print("Successfully clicked on follower button")

        # Don't try to follow users if we already followed them
        # _user_names = [u for u in _user_names if u not in _followed_users]
        # _user_elms = [e for e in driver.find_elements_by_xpath("""//span[contains(text(),'Follow')]""")[1:] if e.text == 'Follow']
        # _user_elms = _user_elms[_num_followed:]
        # for u, e in zip(_user_names, _user_elms):
        #     print("Trying to follow: {}".format(u))
        #     e.click()
        #     print("Successfully followed: {}".format(u))
        #     if env == 'dev':
        #         # Close out of the both that comes up because I don't have an account
        #         time.sleep(2)
        #         # TODO: Fill bare exceptions
        #         try:
        #             driver.find_element_by_xpath("""//*[@id="mount"]/div/div/div[7]/div[2]/*""").click()
        #         except:
        #             try:
        #                 driver.find_element_by_xpath("""/html/body/div[4]/div/div[2]/div/div/svg/path""").click()
        #
        #             except:
        #                 pass
        #         time.sleep(2)
        #         # Refocus the scrolling
        #     try:
        #         driver.find_elements_by_xpath("""//p[contains(text(),'@')]""")[1:][0].click()
        #     except:
        #         print("Could not refocus scrolling element")
        #     scroll_elm.send_keys(Keys.END)

    def follow(self, username):
        print("Following the followers of {}".format(username))
        self.get_user_stats(username)
        self.click_on_follower_list()
        self.follow_from_list()



f = Follower(driver, home_user, env)
# Login
f.nav_to_mainpage()
# Go to home user and get their stats
f.get_user_stats(f.home_user)
f.follow('oldfinds')

# # Enter following mode
# if mode=="following":
#     # TODO: Try to just start following from either the users follower list or following list
#
#     # Click on the user's followers
#     try:
#         user_follower_elm = driver.find_element_by_xpath("""//span[contains(text(),'Followers')]""")\
#             .find_element_by_xpath("..")
#     except:
#         raise FindingElementError("Failed to find follower button on a users page")
#
#     user_follower_num = int(user_follower_elm.text.replace(' Followers', ''))
#
#     # You're probably better off just stopping after a certain amount of time
#     # Rather than a particular number of users
#     break_time = 30
#
#     # Click on the users follower list
#     try:
#         user_follower_elm.click()
#     except:
#         raise ClickError("Failed to click on a list of followers")
#     time.sleep(8)
#
#     # Start following
#     scroll_elm = driver.find_element_by_tag_name('html')
#     new_start_time = time.time()
#     _num_followed = 0
#     _followed_users = []
#     while time.time() - new_start_time < 30:
#         # Click on the follower name to bring the follower list into scope
#         try:
#             elms = driver.find_elements_by_xpath("""//p[contains(text(),'@')]""")[1:]
#         except:
#             raise FindingElementError("Failed to find users in the list (in order to return scope to scroll).")
#
#         try:
#             elms[-1].click()
#         except:
#             raise ClickError("Failed to click the last user (in order to return scope to scroll).)")
#
#         _user_names = [u.text.replace('@', '') for u in driver.find_elements_by_xpath("""//p[contains(text(),'@')]""")]
#
#         # Don't try to follow users if we already followed them
#         _user_names = [u for u in _user_names if u not in _followed_users]
#         _user_elms = [e for e in driver.find_elements_by_xpath("""//span[contains(text(),'Follow')]""")[1:] if e.text == 'Follow']
#         _user_elms = _user_elms[_num_followed:]
#         for u, e in zip(_user_names, _user_elms):
#             print("Trying to follow: {}".format(u))
#             e.click()
#             print("Successfully followed: {}".format(u))
#             if env == 'dev':
#                 # Close out of the both that comes up because I don't have an account
#                 time.sleep(2)
#                 # TODO: Fill bare exceptions
#                 try:
#                     driver.find_element_by_xpath("""//*[@id="mount"]/div/div/div[7]/div[2]/*""").click()
#                 except:
#                     try:
#                         driver.find_element_by_xpath("""/html/body/div[4]/div/div[2]/div/div/svg/path""").click()
#
#                     except:
#                         pass
#                 time.sleep(2)
#                 # Refocus the scrolling
#             try:
#                 driver.find_elements_by_xpath("""//p[contains(text(),'@')]""")[1:][0].click()
#             except:
#                 print("Could not refocus scrolling element")
#             scroll_elm.send_keys(Keys.END)
#
#
#
#
#
#
#
#
#
# if mode=="unfollowing":
#     prof_following_elm.click()
#     time.sleep(3)
#     scroll_elm = driver.find_element_by_tag_name('html')
#     sauce=driver.page_source
#     sauce=sauce.split()
#     sauce=[i for i in sauce if "Following" in i and "span" in i][-1]
#     data_word=sauce.split("=")[0]
#     users_unfollowed=0
#     reset_switch=0
#     while users_unfollowed<prof_following_num:
#         scroll_elm.send_keys(Keys.END)
#         for user in driver.find_elements_by_css_selector("["+data_word+"='']"):
#             try:
#                 user.click()
#                 users_unfollowed=users_unfollowed+1
#                 reset_switch=reset_switch+1
#             except:
#                 pass
#         if reset_switch>300:
#             driver.refresh()
#             prof_following_elm = driver.find_element_by_xpath("""//span[contains(text(),'Following')]""").find_element_by_xpath("..")
#             prof_following_num = int(prof_following_elm.text.replace(' Following',''))
#             prof_following_elm.click()
#             time.sleep(3)
#             users_unfollowed=0
#             reset_switch=0
#             scroll_elm = driver.find_element_by_tag_name('html')
#     print("Done unfollowing.")


if env == 'dev':
    driver.close()
        
