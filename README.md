# Depop
Program to follower and unfollow users

## Warning  

My account was deleted 5/9/2018 citing a violation of the [terms of service](http://explore.depop.com/en/terms/) 
"8. misuse the Service by knowingly introducing viruses, Trojans, worms, logic bombs or other material which would harm the Service or any user of the Service's own equipment;"
I don't think this program falls under that category, but nevertheless I cannot advise anyone use this code.

#### Steps/Requirements to use this code:  

Please read this in its entirety.

1. Install Python (**get any recent version of python3**) (https://www.python.org/downloads/). Personally I use Spyder IDE through Anaconda (https://www.anaconda.com/download/). Be sure to `pip install selenium` or with conda: `conda install selenium`  

2. Install chromedriver (https://sites.google.com/a/chromium.org/chromedriver/downloads). You might be able to use PhantomJS or others, but this is set up for Chrome.  

3. Fork, clone, or copy/paste the code into a Python script. Starring this repo would also be appreciated :)  

3. Define the variable chrome_path to be the path to your chromedriver executable. 
E.g. chrome_driver = r"C:\Users\John_Doe\Downloads\chromedriver_win32\chromedriver.exe"  

4. Change the variable home_user to be your Depop username.  
E.g. home_user = "johndoesclothes"

5. Run the script.  

You will first be prompted to login with your depop credentials. Once you logged in press enter in the Python prompt to continue running the script. You will then be prompted whether you want to follow or unfollow users.  

If you want to follow users type "following" at the Python prompt and press enter. You will then be prompted to give the name of a user which will establish a list of people to follow. Type the name of a user (can be any user, e.g. gsvwear) and press enter. Due to time considerations, only 300 (at most) users are followed from any particular user. Once this number is reached or there are no more users to follow (i.e. the user has less than 300 followers) a new user will be chosen. This method propagates onward until you have followed 7,500 users. I may eventually incorporate a more targeted approach based on hashtags or something else.

If you want to unfollow users (Depop only lets you follow 7,500 users) type "unfollowing" into the Python prompt. This will unfollow all the users you are currently following.  

Note: It is ~~possible~~ evidently the case (as of 5/9/2018) that using this program violates the terms of service for Depop, though I can find no explicit mention of this practice. I am not responsible for any resulting action that comes from using this script (such as the suspension of your account or legal action). I wrote this to see if it would work and so I wouldn't have to personally follow users in order to attract traffic to my account. I should also say that using this will not necessarily increase the sale of your products (though it will probably increase your follower count). Use at your own risk and do not abuse.  


![depop2](https://user-images.githubusercontent.com/29719483/34895127-2d5fcb1e-f799-11e7-81ba-74430260032c.png)
![depop1](https://user-images.githubusercontent.com/29719483/34895125-2d2b2436-f799-11e7-9ce0-bc062547cfb9.png)
