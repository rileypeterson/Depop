# -*- coding: utf-8 -*-
"""
Created on Thu Jul 20 14:28:40 2017

@author: Riley Peterson
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import time
import sys

chrome_path = r"your/chrome/driver/executable.exe" ###Path to your chromedriver executable
driver = webdriver.Chrome(chrome_path)
driver.get('https://www.depop.com/')
time.sleep(3)
[elm.click() for elm in driver.find_elements_by_xpath("""//span[text()="Login"]""") if elm.text=="Login"]      #Clicks login button

input("Type in login details, then press enter, then press enter to continue running script")
mode = input("select mode (following, unfollowing):")


driver.get('https://www.depop.com/yourusernamehere')  #Path to your homepage
#Now at home profile page
time.sleep(3)
elm5 = driver.find_element_by_xpath("""//span[contains(text(),' Following')]""")
num_fol = int(elm5.text.replace(' Following',''))
if mode=="unfollowing":
    elm5.click()
    time.sleep(3)
    elm = driver.find_element_by_tag_name('html')
    list_of_following=driver.find_elements_by_xpath("""//span[text()='Following']""")
    while len(list_of_following)>0:
        for i in list_of_following:
            try:
                if i.is_displayed()==True and i.text=="Following":
                    i.click()
            except:
                pass
        reset_time=time.time()
        while (time.time()-reset_time)<300:
            elm.send_keys(Keys.END)
        list_of_following=driver.find_elements_by_xpath("""//span[text()='Following']""")

        

if mode=="following":
    [elm.click() for elm in driver.find_elements_by_xpath("""//span[text()="Search"]""") if elm.text=="Search"]
    us = input("type username to rip followers from:")
    us = "@"+us
    driver.find_element_by_xpath("""//input[@type='text']""").send_keys(us) #searches for user
    driver.find_element_by_xpath("""//input[@type='text']""").send_keys(Keys.ENTER) #goes to user profile
    time.sleep(3)
    end = int(driver.find_element_by_xpath("""//span[contains(text(),' Followers')]""").text.replace(" Followers",""))
    elm5 = driver.find_element_by_xpath("""//span[contains(text(),' Followers')]""")
    elm5.click()
    time.sleep(5)
    if end+num_fol>7500:
        end=7500-num_fol
    else:
        pass
    k=0
    m=0
    file = open('people_ive_followed.txt','r')
    txt = file.readlines()
    followed_people=[]
    for line in txt:
        followed_people.append(line.strip())
    while k<end:
        j = driver.find_elements_by_xpath("""//span[text()='Follow']""")[1:] #possible people to follow
        y = driver.find_elements_by_xpath("""//p[text()='@']""")[1:] #names of people
        n = len(j)
        print("j is "+str(n)+" long")
        print('clicking mode')
        file1 = open('people_ive_followed.txt','a')
        for i in range(m,n):
            print("we are on:"+str(y[i].text))
            try:
                if j[i].text=='':
                    print('j[i].text equals null at i equals', i)   #Already following case
                    print('Already following: ', y[i].text)
                if j[i].text=='Follow' and y[i].text not in followed_people:    #Not/Haven't Following/Followed
                    j[i].click()
                    print('We followed: ', y[i].text)
                    file1.write(y[i].text)
                    file1.write('\n')
                if j[i].text=='Follow' and y[i].text in followed_people:
                    k=k-1
                    print('Already followed in the past: ', y[i].text)
            except:
                print('SOMETHING WEIRD HAPPENED')
            k=k+1
        file1.close()
        f=len(j)+20
        print('f is',f)
        print('scrolling mode')
        old_time = time.time()
        while len(j)<f:
            elm = driver.find_element_by_tag_name('html')
            elm.send_keys(Keys.END)
            elm.send_keys(Keys.END)
            elm.send_keys(Keys.END)
            print('scroll')
            time.sleep(3)
            j = driver.find_elements_by_xpath("""//span[text()='Follow']""")[1:]
            y = driver.find_elements_by_xpath("""//p[text()='@']""")[1:]
            print('the len of j is now '+str(len(j)))
            print('length j less than '+str(f))
            if (time.time()-old_time)>300:
                print('took too long')
                print('k is:'+str(k))
                k=100000000
                break
        print('k is '+str(k))
        m=n



