"""
Program to follow and unfollow users for Depop.

"""

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


# Exceptions
def UserLandingPageError(Exception):
    """ Failed to connect to the users page """
    pass

def ClickError(Exception):
    """ Failed to click on an element """
    pass

def FindingElementError(Exception):
    """ Failed to find an element """
    pass

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
    SUCCESSFUL_UNFOLLOW_MESSAGE = "Successfully unfollowed {}! Have unfollowed {} user(s)."
    def __init__(self, driver, home_user="", env='prod'):
        print("Starting Depop Follower...")
        self.driver = driver
        self.total_users_followed = 0
        self.total_users_unfollowed = 0
        self.mode = None
        self.env = env
        self.home_user = home_user
        self.home_user_num_followers = 0
        self.home_user_num_following = 0
        self.on_user_page = False
        self.on_follower_list = False
        self.on_following_list = False
        self.home_user_logged_in = False
        self.current_username_num_followers = 0
        self.current_username_num_following = 0
        self.followed_users = []
        self.unfollowed_users = []
        self.window_size = None
        self.set_env()

    def set_env(self):
        """
        Set additional parameters in the init of the Follower class.

        """
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
            return
        # I'm lazy
        self.current_username = 'gsvwear'
        self.mode = 'following'

    def reinitialize_on_user_page(self):
        """
        Reset attributes when navigating to the user page.

        """
        self.on_user_page = True
        self.on_follower_list = False
        self.on_following_list = False

    def find_element(self, _callable, arg, error=""):
        """
        Find a single element. If incapable of being found, display a useful error message.

        Parameters
        ----------
        _callable : callable
            The driver method being used to find the element (e.g. driver.find_element_by_xpath).
        arg : str
            Pattern to be search for when finding the element.
        error : str, optional
            Error message (Selenium error messages are often not very obvious).

        Returns
        -------
        selenium.webdriver.remote.webelement.WebElement

        """
        if not error:
            error = "Failed to find an element with string arg {}".format(arg)
        try:
            ret = _callable(arg)
        except Exception as e:
            print(error)
            raise e
        return ret

    def find_elements(self, _callable, arg, error=""):
        """
        Find a list of elements. If incapable of being found, display a useful error message.

        Parameters
        ----------
        _callable : callable
            The driver method being used to find the elements (e.g. driver.find_element_by_xpath).
        arg : str
            Pattern to be search for when finding the elements.
        error : str, optional
            Error message (Selenium error messages are often not very obvious).

        Returns
        -------
        list [selenium.webdriver.remote.webelement.WebElement]

        """
        if not error:
            error = "Failed to find elements with string arg {}".format(arg)
        try:
            ret = _callable(arg)
        except Exception as e:
            print(error)
            raise FindingElementError(error)
        return ret

    def click_elm(self, elm, error=""):
        """
        Try to click and element. Display a meaningful error message if unsuccessful.
        Parameters
        ----------
        elm : selenium.webdriver.remote.webelement.WebElement
            The element to be clicked.
        error : str, optional
            The meaningful error message to display.

        """
        if not error:
            error = "Failed to click element with text {}".format(elm.text)
        try:
            elm.click()
        except Exception as e:
            print(error)
            raise e

    def nav_to_user(self, username=None):
        """
        Navigate to a user's page.
        Parameters
        ----------
        username : str, optional
            Username of the user to navigate to.

        """
        if not username:
            username = self.current_username
        self.driver.get(self.BASE_URL + username)
        self.reinitialize_on_user_page()

    def nav_to_login_page(self):
        """
        Navigate to the login page so the user can login with their credentials.

        """
        # Make the driver and navigate to the depop main page.
        if env == 'prod':
            # If in production we should login
            self.driver.get(self.LOGIN_URL)
            input("Type in login details, then press enter, then press enter to continue running script")
            self.home_user_logged_in = True

    def _get_following_elm(self):
        """
        Return the element that can be clicked to bring up the list of users that a user is following.
        Returns
        -------
        selenium.webdriver.remote.webelement.WebElement

        """
        following_elm_child = self.find_element(self.driver.find_element_by_xpath,
                                           """//span[contains(.,'Following')]""",
                                           error="Couldn't find Following element child")
        # TODO: Must be a better way
        try:
            following_elm_parent = following_elm_child.find_element_by_xpath("..")
        except Exception as e:
            print("Failed to find following element parent")
            raise e
        return following_elm_parent

    # TODO: Refactor. Combine with above definition
    def _get_follower_elm(self):
        """
        Return the element that can be clicked to bring up the list of users that are following a user (followers).
        Returns
        -------
        selenium.webdriver.remote.webelement.WebElement

        """
        follower_elm_child = self.find_element(self.driver.find_element_by_xpath,
                                           """//span[contains(.,'Followers')]""",
                                           error="Couldn't find Follower element child")
        # TODO: Must be a better way.
        try:
            follower_elm_parent = follower_elm_child.find_element_by_xpath("..")
        except Exception as e:
            print("Failed to find follower element parent")
            raise e
        return follower_elm_parent

    def print_elm_attrs(self, elm):
        """
        Print out attributes of element.
        Parameters
        ----------
        elm : selenium.webdriver.remote.webelement.WebElement

        """
        print("Location: ", elm.location,
              "Size: ", elm.size,
              "Text: ", elm.text,
              "Is selected:", elm.is_selected(),
              "Is enabled:", elm.is_enabled())


    # TODO: These next few sections are pretty meaty. Could use a refactor.
    def get_user_stats(self, username=None):
        """
        Obtain/set particular stats about a specific user (how many they follow, how many followers).
        Parameters
        ----------
        username : str
            Username to get stats for.

        """
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
        """
        Try (several times) to bring up on screen the list of followers.

        """
        self.click_elm(self._get_follower_elm())
        elms = []
        total_time = time.time()
        # TODO: Refactor. There are better ways to implement a timeout... you can use the timeout elsewhere
        # This could be much simpler... disappointed in myself
        st = time.time()
        while (time.time() - st) < 20:
            while not elms:
                elms = self.find_elements(driver.find_elements_by_xpath, """//p[contains(.,'@')]""")[1:]
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
        """
        Try (several times) to bring up on screen the list of following users.

        """
        # TODO: Refactor. Combine with above and generally make better.
        self.click_elm(self._get_following_elm())
        elms = []
        total_time = time.time()
        st = time.time()
        while (time.time() - st) < 20:
            while not elms:
                elms = self.find_elements(driver.find_elements_by_xpath, """//p[contains(.,'@')]""")[1:]
                time.sleep(1)
            if elms:
                break
            else:
                if (time.time() - total_time) > 100:
                    raise TimeoutError("Failed to click on following list")
                driver.navigate().refresh()
                self.click_elm(self._get_following_elm())
                st = time.time()
        print("Following list loaded successfully")

    def _get_unames_and_fol_btns(self, leading_ind, text="Follow"):
        """
        With the list of followers/following open, return the usernames and clickable follow/following elements
        which are within the scrollable view.
        Parameters
        ----------
        leading_ind : int
            The list of elements will include all the elements in the scrollable section, the leading index
            is used to slice this to exclude elements already followed/unfollowed.
        text : str, optional
            The text ('Follow', 'Following') which is located in the element which can be clicked to follow/unfolllow
            a user.

        Returns
        -------
        unames: list [str]
            The list of usernames.
        follow_btn_elms: list [selenium.webdriver.remote.webelement.WebElement]
            The list of follow/unfollow button elements.

        """
        name_elms = self.find_elements(driver.find_elements_by_xpath, """//p[contains(.,'@')]""",
                                       "Could not get name elms")[leading_ind:]
        # Rescope the follower list
        # self.click_elm(name_elms[-1])
        follow_btns_elms = self.find_elements(driver.find_elements_by_xpath, """//span[contains(.,'{}')]""".format(text),
                                              "Could not get {} button elms".format(text))[leading_ind:]
        follow_btns_elms = [e for e in follow_btns_elms if e.text == "{}".format(text)]
        unames = [e.text.replace('@', '') for e in name_elms]
        return unames, follow_btns_elms

    # TODO: Should be private...
    def handle_not_login_error(self, fol_btn, uname):
        """
        Handle the error the occurs when a user (me) tries to use this program without being logged in.
        Parameters
        ----------
        fol_btn : selenium.webdriver.remote.webelement.WebElement
            The 'Follow' element which invokes the not being logged in popup.
        uname : str
            Username.

        """
        print("Trying to click out of alert")
        try:
            action = webdriver.common.action_chains.ActionChains(self.driver)
            self.window_size = self.driver.get_window_rect()
            click_spot = int(0.9 * (self.window_size['width'] - fol_btn.location['x']))
            action.move_to_element_with_offset(fol_btn, click_spot, 0).click().perform()
            print("Attempting click again")
            self.click_elm(fol_btn)
            if self.mode == 'unfollowing':
                self.unfollowed_users.append(uname)
            else:
                print(self.SUCCESSFUL_FOLLOW_MESSAGE.format(uname, self.total_users_followed))
                self.followed_users.append(uname)
        except Exception as e:
            raise e

    # TODO: These last ones are so ugly it's not work writing docstrings for
    # URGENT
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

    def unfollow(self, timeout=60):
        self.click_on_following_list()
        leading_ind = 1
        st = time.time()
        print('Getting scroll element')
        scroll_elm = self.find_element(driver.find_element_by_tag_name, 'html', "Couldn't find scroll_elm")
        print('Getting usernames and following buttons')
        unames, unfollowing_btns_elms = self._get_unames_and_fol_btns(leading_ind, text="Following")
        print(unames, unfollowing_btns_elms)
        assert len(unfollowing_btns_elms) > 0, "Couldn't find any unfollowing button elements :( ..."
        zipper = zip(unames, unfollowing_btns_elms)
        while (time.time() - st) < timeout and self.home_user_num_following > 3:
            for uname, unfol_btn in zipper:
                print("Attempting to unfollow {}".format(uname))
                print("Attempting click on unfollower button")
                try:
                    self.click_elm(unfol_btn)
                    leading_ind += 1
                    self.total_users_unfollowed += 1
                    self.unfollowed_users.append(uname)
                    self.home_user_num_following -= 1
                    print(self.home_user_num_following)
                    print(self.SUCCESSFUL_UNFOLLOW_MESSAGE.format(uname, self.total_users_unfollowed))
                except Exception as e:
                    if str(e).startswith("Message: unknown error: Element <span>...</span> is not clickable at point"):
                        leading_ind += 1
                        self.total_users_unfollowed += 1
                        self.handle_not_login_error(unfol_btn, uname)
                    else:
                        raise e
                time.sleep(random.random())
            scroll_elm.send_keys(Keys.END)
            unames, unfollowing_btns_elms = self._get_unames_and_fol_btns(leading_ind, text="Following")
            print(unames, unfollowing_btns_elms)
            zipper = zip(unames, unfollowing_btns_elms)




if __name__ == '__main__':
    # Init
    f = Follower(driver, home_user, env)

    # Login
    f.nav_to_login_page()

    # Go to home user and get their stats
    f.get_user_stats(f.home_user)

    if f.mode == 'following':
        f.follow(f.current_username)

    # Think this should work... can't test though
    # Unfollow users for 60 seconds, refresh and repeat until down to 3 users
    elif f.mode == 'unfollowing':
        while f.home_user_num_following > 3:
            f.unfollow()
            print('Pausing for 3 seconds')
            time.sleep(3)
            f.get_user_stats(f.home_user)
            print('Pausing for 3 seconds')
            time.sleep(3)

