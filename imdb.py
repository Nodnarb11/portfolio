#import libraries
import requests
from requests import get  
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time


# base url for use later with next page href
base = 'http://www.imdb.com'

# Create empty lists to store data
titles = []
years = []
times = []
ratings = []
metascores = []
votes = []
gross = []
# add header to make sure web page is in english
headers = {"Accept-Language": "en-US, en;q=0.5"}

# starting url to scrap
url = "http://www.imdb.com/search/title?groups=top_1000&ref_=adv_prv"

#get data from url
results = requests.get(url, headers=headers)

#read the data with BeautifulSoup
soup = BeautifulSoup(results.text, "html.parser")

#Find the next page link
next = soup.find("a", {"class": "lister-page-next next-page"}).get("href")

#Find all the movies on the page
movie_divs = soup.find_all("div", class_="lister-item mode-advanced")

#Make a counter and a while loop to loop through all the pages
counter = 0
while counter != 20:
    print(f'scraping {url}')
    #sleep for 2 seconds
    time.sleep(2)
    for container in movie_divs:
        # extract the title
        title = container.h3.a.text
        titles.append(title)
        # extract the year
        year = container.h3.find('span', class_="lister-item-year").text
        years.append(year)
        # extract the runtime
        runtime = container.p.find("span", class_="runtime").text if container.p.find("span", class_="runtime").text else '0'
        times.append(runtime)
        # extract the rating
        rating = container.strong.text
        ratings.append(rating)
        # extract the metascore
        metascore = container.find("span", class_="metascore").text if container.find("span", class_="metascore") else '0'
        metascores.append(metascore)
        #here are two nv containers grab the votes and gross
        nv = container.find_all("span", attrs={"name": "nv"})
        # extract the votes
        votes.append(nv[0].text)
        # extract the gross
        grosses = nv[1].text if len(nv) > 1 else '0'
        gross.append(grosses)
    # increses the counter by 1
    counter += 1
    # check if counter is less than 19
    if counter < 19:
        url = base + next
        results = requests.get(url, headers=headers)
        soup = BeautifulSoup(results.text, "html.parser")
        movie_divs = soup.find_all("div", class_="lister-item mode-advanced")
        next = soup.find("a", {"class": "lister-page-next next-page"}).get("href")
        print(f'Going to next page {url}')
        print('-' * 40)
    # check if counter is equal to 19
    elif counter == 19:
        url = base + next
        results = requests.get(url, headers=headers)
        soup = BeautifulSoup(results.text, "html.parser")
        movie_divs = soup.find_all("div", class_="lister-item mode-advanced")
        print('last page!')
        print('-' * 40)
    # check if counter is equal to 20    
    elif counter == 20:
        print('done!')
        print('-' * 40)
       # put all list into a csv file and save it
        df = pd.DataFrame(
            {
                "title": titles,
                "year": years,
                "runtime": times,
                "rating": ratings,
                "metascore": metascores,
                "votes": votes,
                "gross": gross
            }
        )
        #clean all the data
        df['year'] = df['year'].str.extract('(\d+)').astype(int)
        df['runtime'] = df['runtime'].str.extract('(\d+)').astype(int)
        df['metascore'] = df['metascore'].astype(int)
        df['votes'] = df['votes'].str.replace(',', '').astype(int)
        df['gross'] = df['gross'].map(lambda x: x.lstrip('$').rstrip('M'))
        df['gross'] = pd.to_numeric(df['gross'], errors='coerce')


        #print(df.head())
        # save df as a csv file
        df.to_csv("imdb_top_1000.csv", index=False)







