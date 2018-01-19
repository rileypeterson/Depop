from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import random
import time
import sys


chrome_path = r"your\path\to\chromedriver.exe"
driver = webdriver.Chrome(chrome_path)
driver.get('https://www.depop.com/')
time.sleep(3)
[elm.click() for elm in driver.find_elements_by_xpath("""//span[text()="Login"]""") if elm.text=="Login"]      #Clicks login button
home_user="yourusernamehere"
input("Type in login details, then press enter, then press enter to continue running script")
mode = input("select mode (following, unfollowing):")


driver.get('https://www.depop.com/'+home_user)
#Now at home profile page
time.sleep(3)
prof_following_elm = driver.find_element_by_xpath("""//span[contains(text(),'Following')]""").find_element_by_xpath("..")
prof_following_num = int(prof_following_elm.text.replace(' Following',''))
prof_follower_elm = driver.find_element_by_xpath("""//span[contains(text(),'Followers')]""").find_element_by_xpath("..")
prof_follower_num = int(prof_follower_elm.text.replace(' Followers',''))
if mode=="unfollowing":
    prof_following_elm.click()
    time.sleep(3)
    scroll_elm = driver.find_element_by_tag_name('html')
    sauce=driver.page_source
    sauce=sauce.split()
    sauce=[i for i in sauce if "data" in i and "Following" in i and "span" in i][-1]
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

if mode=="following":
    prof_follower_elm.click()
    time.sleep(3)
    sauce=driver.page_source
    sauce=sauce.split()
    sauce=[i for i in sauce if "data-css" in i and "Follow" in i and "span" in i]
    sauce=list(set(sauce))
    break_button_1="no"
    while break_button_1=="no":
        for data in sauce:
            scroll_elm = driver.find_element_by_tag_name('html')
            driver.find_elements_by_xpath("""//p[contains(text(),'@')]""")[1:][0].click()
            scroll_elm.send_keys(Keys.END)
            data_word=data.split("=")[0]
            buttons=driver.find_elements_by_css_selector("["+data_word+"='']")[1:]
            for button in buttons:
                if button.text=="Follow" and button.is_displayed():
                    break_button_1="yes"
                    break
            if break_button_1=="yes":
                break
        sauce=driver.page_source
        sauce=sauce.split()
        sauce=[i for i in sauce if "data-css" in i and "Follow" in i and "span" in i]
        sauce=list(set(sauce))
    print(data_word)
    def rip_followers(username,data_word,prof_following_num,total_users_followed=0):
        driver.get('https://www.depop.com/'+username)
        user_follower_elm = driver.find_element_by_xpath("""//span[contains(text(),'Followers')]""").find_element_by_xpath("..")
        user_follower_num = int(user_follower_elm.text.replace(' Followers',''))
        if user_follower_num>300:
            user_follower_num=300
        user_follower_elm.click()
        time.sleep(8)
        scroll_elm = driver.find_element_by_tag_name('html')
        new_start_time=time.time()
        while time.time()-new_start_time<30:
            try:
                driver.find_elements_by_xpath("""//p[contains(text(),'@')]""")[1:][0].click()
                break
            except:
                pass
        users_followed,break_button=0,"no"
        while users_followed<user_follower_num:
            scroll_elm.send_keys(Keys.END)
            follow_buttons=driver.find_elements_by_css_selector("["+data_word+"='']")[1:]
            usernames=driver.find_elements_by_xpath("""//p[contains(text(),'@')]""")[1:]
            for user in follow_buttons:
                try:
                    user.click()
                    users_followed=users_followed+1
                    total_users_followed=total_users_followed+1
                    if total_users_followed+prof_following_num>=7499:
                        break_button="yes"
                        break
                except:
                    pass
            scroll_elm.send_keys(Keys.END)
            if len(follow_buttons)==len(driver.find_elements_by_css_selector("["+data_word+"='']")[1:]):
                start_time=time.time()
                while time.time()-start_time<5:
                    scroll_elm.send_keys(Keys.END)
                    if len(follow_buttons)!=len(driver.find_elements_by_css_selector("["+data_word+"='']")[1:]):
                        break_button_2="no"
                        break
                    else:
                        break_button_2="yes"
                if break_button_2=="yes":
                    break
            if break_button=="yes":
                print("hit break button")
                break
        print("Done following "+username+" followers. Followed "+str(users_followed)+" users.")
        text_usernames=[i.text.replace("@","") for i in usernames[:25]]
        return text_usernames,users_followed,break_button,total_users_followed
    total_users_followed=0
    username=input("First username to use:")
    break_button="no"
    while break_button=="no":
        new_users,dummy,break_button,total_users_followed=rip_followers(username,data_word,prof_following_num,total_users_followed=total_users_followed)
        random.shuffle(new_users)
        user_follower_num,j=0,0
        while user_follower_num==0:
            nombre=new_users[j]
            driver.get('https://www.depop.com/'+nombre)
            user_follower_elm = driver.find_element_by_xpath("""//span[contains(text(),'Followers')]""").find_element_by_xpath("..")
            user_follower_num = int(user_follower_elm.text.replace(' Followers',''))
            if user_follower_num>10:
                username=nombre
                break
            j=j+1
        
        
