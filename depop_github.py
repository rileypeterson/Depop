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
    LOGIN_URL = 'https://www.depop.com/login'
    MAX_USERS = 7499
    SUCCESSFUL_FOLLOW_MESSAGE = "Successfully followed {}! Have followed {} user(s)."
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
            self.mode = input("select mode (following, unfollowing):")
            assert self.mode == 'following' or self.mode == 'unfollowing', \
                "Unrecognized mode. Possible mode are 'following' or 'unfollowing'"
            if self.mode == 'following':
                # If following ask for a first user name to follow
                self.current_username = input("First username to use:")
            else:
                # Because we're going to unfollow...
                self.current_username = self.home_user
        else:
            # I'm lazy
            self.current_username = 'gsvwear'
            self.mode = 'following'
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
        if env == 'prod':
            # If in production we should login
            self.driver.get(self.LOGIN_URL)
            input("Type in login details, then press enter, then press enter to continue running script")
            self.home_user_logged_in = True

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
        time.sleep(1)
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
        print("\n{} is following {} user(s) "
              "and have {} follower(s).\n".format(username,
                                                self.current_username_num_following,
                                                self.current_username_num_followers))

    def click_on_follower_list(self):
        self.click_elm(self._get_follower_elm())
        elms = []
        total_time = time.time()
        st = time.time()
        while (time.time() - st) < 20:
            while not elms:
                elms = self.find_elements(driver.find_elements_by_xpath, """//p[contains(text(),'@')]""")[1:]
                time.sleep(1)
            if elms:
                break
            else:
                if (time.time() - total_time) > 100:
                    raise TimeoutError("Failed to click on follower list")
                driver.navigate().refresh()
                self.click_elm(self._get_follower_elm())
                st = time.time()
        print("Follower list loaded successfully")

    def click_on_following_list(self):
        self.click_elm(self._get_following_elm())

    def _get_unames_and_fol_btns(self, leading_ind):
        name_elms = self.find_elements(driver.find_elements_by_xpath, """//p[contains(text(),'@')]""",
                                       "Could not get name elms")[leading_ind:]
        # Rescope the follower list
        # self.click_elm(name_elms[-1])
        follow_btns_elms = self.find_elements(driver.find_elements_by_xpath, """//span[contains(text(),'Follow')]""",
                                              "Could not get follow button elms")[leading_ind:]
        follow_btns_elms = [e for e in follow_btns_elms if e.text == "Follow"]
        unames = [e.text.replace('@', '') for e in name_elms]
        return unames, follow_btns_elms

    def handle_not_login_error(self, fol_btn, uname):
        print("Trying to click out of alert")
        try:
            action = webdriver.common.action_chains.ActionChains(self.driver)
            self.window_size = self.driver.get_window_rect()
            click_spot = int(0.9 * (self.window_size['width'] - fol_btn.location['x']))
            action.move_to_element_with_offset(fol_btn, click_spot, 0).click().perform()
            print("Attempting click again")
            self.click_elm(fol_btn)
            print(self.SUCCESSFUL_FOLLOW_MESSAGE.format(uname, self.total_users_followed))
            self.followed_users.append(uname)
        except Exception as e:
            raise e

    def follow_from_list(self, max_num=50, timeout=60):
        max_to_follow = min(max_num, self.current_username_num_followers)
        st = time.time()
        i = 1
        leading_ind = 1
        scroll_elm = self.find_element(driver.find_element_by_tag_name, 'html', "Couldn't find scroll_elm")

        unames, follow_btns_elms = self._get_unames_and_fol_btns(leading_ind)
        zipper = zip(unames, follow_btns_elms)
        while i < max_to_follow and (time.time() - st) < timeout:
            for uname, fol_btn in zipper:
                if i > max_to_follow:
                    break
                if uname not in self.followed_users:
                    print("Attempting to follow {}".format(uname))
                    print("Attempting click on follower button")
                    try:
                        self.click_elm(fol_btn)
                        i += 1
                        leading_ind += 1
                        self.total_users_followed += 1
                        self.followed_users.append(uname)
                        print(self.SUCCESSFUL_FOLLOW_MESSAGE.format(uname, self.total_users_followed))
                    except Exception as e:
                        if str(e).startswith("Message: unknown error: Element <span>...</span> is not clickable at point"):
                            i += 1
                            leading_ind += 1
                            self.total_users_followed += 1
                            self.handle_not_login_error(fol_btn, uname)
                        else:
                            raise e
                time.sleep(random.random())
            scroll_elm.send_keys(Keys.END)
            unames, follow_btns_elms = self._get_unames_and_fol_btns(leading_ind)
            zipper = zip(unames, follow_btns_elms)
        unames, follow_btns_elms = self._get_unames_and_fol_btns(0)
        return unames
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
        unames = [username]
        while self.total_users_followed < self.MAX_USERS:
            u = random.choice(unames)
            print("Potentially following the followers of {}".format(u))
            retries = 0
            while retries < 4:
                try:
                    self.get_user_stats(u)
                    break
                except:
                    print("Failed to get user stats retrying")
                    retries += 1
            # If less than 10 it's not really worth it...
            if self.current_username_num_followers > 10:
                self.click_on_follower_list()
                time.sleep(random.random())
                unames = self.follow_from_list()
            elif self.current_username_num_followers <= 10 and self.total_users_followed == 0:
                raise ValueError("The first user you want to follow needs to have more than 10 followers.")



f = Follower(driver, home_user, env)
# Login
f.nav_to_mainpage()
# Go to home user and get their stats
f.get_user_stats(f.home_user)
f.follow(f.current_username)

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
        
