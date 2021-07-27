#!/usr/bin/env python
# coding: utf-8

# In[1]:


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

# from chromedriver_py import binary_path add as executable path in webdriver.Chrome
from webdriver_manager.chrome import ChromeDriverManager

import vlc
import pafy

import pandas as pd
import re
import time

site="https://www.youtube.com/"
youtube_search="results?search_query="
youtube_watch= "watch?v="

url_youtube_search=site+youtube_search
url_youtube_watch=site+youtube_watch

#youtube search URL format "results?search_query=enter+your+search"
print("==========WELCOME TO YT-PLAYER==========")
print(" ")
search= "+".join(input("Hi! What are you looking for?\n\nSEARCH:").split(" "))
query= url_youtube_search+search
print("\nGot it! Just a moment...\n")


# In[2]:


#gain access and extract the information
def info_to_df(query):
    """accepts terms and conditions and organize the infromation extract into a dataframe"""
    
#     options = webdriver.ChromeOptions()
#     options.add_argument("--start-minimized")

    driver=webdriver.Chrome(ChromeDriverManager().install())
    driver.minimize_window()
    driver.get(query)
    
    #agree to terms
    time.sleep(1)
    button=driver.find_elements_by_xpath("//button[@jsname='higCR' and @aria-label='Agree to the use of cookies and other data for the purposes described']")[0]
    
    time.sleep(2)
    button.click()

    # get info about the video and the author
    videoTitle=driver.find_elements_by_xpath("//a[@id='video-title']")
    time.sleep(2)
    authorInfo=driver.find_elements_by_xpath("//a[@class='yt-simple-endpoint style-scope yt-formatted-string']")

    time.sleep(1)
    
    # extract attributes fro prev search
    videoList=[[index+1, video.get_attribute('href'), video.get_attribute('title')] for index, video in enumerate(videoTitle)]
    authorList=[[info.text, info.get_attribute('href')] for index, info in enumerate(authorInfo) if index %2 != 0]

    time.sleep(1)

    #organize data into a DF
    youtube=pd.concat([pd.DataFrame(data=videoList, columns=["index", "videoLink", "title"]),                       pd.DataFrame(data=authorList, columns=["author", "channelLink"])],                       axis=1).head(16)
    
    driver.close()
    driver.quit()
    
    ###########################################################################
    
    def get_video_id(string):
        try:
            string=re.sub(r"\w+://\w+\.\w+\.\w+\/\w+\?\w\=", "", string)
        except:
            pass
        return string

    def get_channel_path(string):
        try:
            string=re.sub(r"\w+://\w+\.\w+\.\w+\/","",string)
        except:
            pass
        return string
    
    #############################################################################


    youtube["videoId"]=youtube["videoLink"].map(get_video_id)
    youtube["channelPath"]=youtube["channelLink"].map(get_channel_path)
    
    youtube.drop(["videoLink", "channelLink"], axis=1, inplace=True)
 
    #############################################################################
    
    def make_choice(df):
        
        """Main menu containing the research results"""
        
        valid_response=['download','listen','D','L']
        tracks=[]

        print("\n\nHey! Look what I found:\n\n")

        for index, song in enumerate(df["title"]):
            tracks.append(song)
            print("ID: {} - TITLE: {}".format(index, song))

        print(" ")
        row=input("Which one you want to explore?\nType its ID: ")
        
        if row.isalpha():
            print("\nPlease, insert the track's ID!\n")
            make_choice(df)
            
        if row.isnumeric():
            row=int(row)
            if row >= len(tracks):
                print("\nPlease, insert a valid command!\n")
                info_to_df(query)
            
        print(" ")     
        operation=input("Choose your option:\n[download(D)|listen(L)]: ")
        
        if operation in valid_response:
            operation=operation
        else:
            print("\nPlease, insert a valid command!\n")
            info_to_df(query)
        
        return (row, operation)
    
    
    def converter(row_id):

        """Accepts a youtube video ID and downloads it in mp3"""

        convert_web="https://youtubetomp3music.com/en13/download?url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D"


        driver=webdriver.Chrome()
        driver.minimize_window()
        driver.get(convert_web + youtube.loc[int(row_id), "videoId"])

        button_convert=driver.find_element_by_xpath("//button[@id='cvt-btn']")
        button_convert.click()  

        time.sleep(2)
        try:
            WebDriverWait(driver, 60).until(ec.presence_of_element_located((By.XPATH, "//a[@id='mp3-dl-btn']")))
        except:
            time.sleep(3)
                 
        WebDriverWait(driver, 30).until(ec.presence_of_element_located((By.XPATH, "//a[@id='mp3-dl-btn']"))) 
        
        time.sleep(2)
        
        try:
            download_button=driver.find_element_by_xpath("//a[@id='mp3-dl-btn']")
        except:
            time.sleep(6)
            
        download_button=driver.find_element_by_xpath("//a[@id='mp3-dl-btn']")
        
        download_link=download_button.get_attribute('href')

        time.sleep(2)

#         youtube['downloadLink']=download_link
        driver.get(download_link)
    
        time.sleep(10)
        
        driver.close()
        driver.quit()
        
                
    def close_process(df):

        """Ask the user if to continue or exit"""

        print(" ")
        for index, song in enumerate(df["title"]):
            print("ID: {} - TITLE: {}".format(index, song))

        print(" ")
        choice=input("Would you like to continue with this search?\n[Y/N]: ")

        if choice=="Y":
            row, operation = make_choice(youtube)
            while True:
                new_url=url_youtube_watch+youtube.loc[int(row), "videoId"]

                video=pafy.new(new_url)

                best=video.getbestaudio()

                media=vlc.MediaPlayer(best.url)

                valid_response=['P', 'R', 'M', 'D']

                if operation=="listen" or operation=='L':
                    print(" ")
                    print("listening to {}...\n".format(youtube.loc[int(row), "title"]))

                    media.play()
                    start_time=time.time()
                    duration=media.get_length()/1000

                    while start_time != duration:

                        print('\nPress P to Pause')
                        print('Press R to Resume')
                        print('Press D to Download')
                        print('Press M to Menu\n')

                        command=input('PAUSE(P), RESUME(R), DOWNLOAD(D), MENU(M): ')    

                        if command not in valid_response:
                            print('Please, insert a valid response.')

                        else:

                            if command=='P':
                                media.set_pause(1)
                                print('PAUSED')
                            elif command=='R':
                                media.play()
                                print('Back to it')
                            elif command=='D':
                                converter(row)
                                print(" ")
                                print("downloading {}...\n".format(youtube.loc[int(row), "title"]))
                            elif command=='M':
                                media.stop()
                                prin"\n==========WELCOME TO YT-PLAYER=========="
                                print(" ")
                                search= "+".join(input("Hi! What are you looking for?\n\nSEARCH:").split(" "))
                                query= url_youtube_search+search
                                print("\nGot it! Just a moment...\n")
                                info_to_df(query)

                if operation=="download" or operation=='D':
                    print(" ")
                    print("downloading {}...\n".format(youtube.loc[int(row), "title"]))
                    choice=converter(row)

                close_process(youtube)


        if choice=="N":
            run=True
            while run:
                closure=input("Would you like to discover more or exit?\n[more/exit]: ")

                if closure == "exit":
                    print("\nMMMMKAY, BYE!")
                    run=False
                    quit()
                    break

                if closure == "more":
                    print("\n==========WELCOME TO YT-PLAYER==========")
                    print(" ")
                    search= "+".join(input("Hi! What are you looking for?\n\nSEARCH:").split(" "))
                    query= url_youtube_search+search
                    print("\nGot it! Just a moment...\n")
                    info_to_df(query)
        else:
            print("\nPlease, insert a valid response.\n")
            close_process(df)
            
    ###################################################################################################
    
    row, operation = make_choice(youtube)
    
    while True:
        new_url=url_youtube_watch+youtube.loc[int(row), "videoId"]

        video=pafy.new(new_url)

        best=video.getbestaudio()

        media=vlc.MediaPlayer(best.url)

        valid_response=['P', 'R', 'M', 'D']
            
        if operation=="listen" or operation=='L':
            print(" ")
            print("listening to {}...\n".format(youtube.loc[int(row), "title"]))
            
            media.play()
            start_time=time.time()
            duration=media.get_length()/1000
            
            while start_time != duration:
            
                print('\nPress P to Pause')
                print('Press R to Resume')
                print('Press D to Download')
                print('Press M to Menu\n')

                command=input('PAUSE(P), RESUME(R), DOWNLOAD(D), MENU(M): ')    

                if command not in valid_response:
                    print('Please, insert a valid response.')

                else:

                    if command=='P':
                        media.set_pause(1)
                        print('PAUSED')
                    elif command=='R':
                        media.play()
                        print('Back to it')
                    elif command=='D':
                        converter(row)
                        print(" ")
                        print("downloading {}...\n".format(youtube.loc[int(row), "title"]))
                    elif command=='M':
                        media.stop()
                        close_process(youtube)
                        break


        if operation=="download" or operation=='D':
            print(" ")
            print("downloading {}...\n".format(youtube.loc[int(row), "title"]))
            choice=converter(row)
            
        
        break


        


# In[3]:


try:
    info_to_df(query)
except KeyboardInterrupt:
    pass


# In[ ]:




