
#Final Project CSCI 182**

"""Beautiful Soup Approach"""

import requests
import numpy as np
import pandas as pd
from urllib.request import Request, urlopen
#from selenium import webdriver

from random import randint
from time import sleep
from bs4 import BeautifulSoup

spreadSheet = "final_project_cars - Sheet1"
URL1 = "https://www.kbb.com/"
URL2 = "https://www.carmax.com/"
#URL3 = "https://www.autotrader.com/" ---> not using this website because it has duplicate info from kbb.com
URL4 = "https://www.cars.com/"
inspected_cars = pd.read_csv(spreadSheet + ".csv")
cars_lst_missing_info = {}

print(inspected_cars)

"""**Selenium Approach**"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time


options = webdriver.ChromeOptions()

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'
options.add_argument('user-agent={0}'.format(user_agent))
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

s = Service('C:\Program Files (x86)\Google\chromedriver.exe')
DRIVER_PATH = 'C:\Program Files (x86)\Google\chromedriver.exe'

"""Set-up columns and index for pandas dataframe"""

#column labels and sub column labels for the csv file written to
columns = [
           ['car','car','rating','rating','rating','rating','rating','rating','rating','rating','rating','rating','rating','rating','rating','rating','rating','rating','rating','rating','rating','rating','rating','rating','rating','rating','rating','rating','rating','rating','pros','pros','pros','cons','cons','cons'],
           ['brand','price','consumer','consumer','consumer','consumer','value', 'value', 'value','value','performance', 'performance', 'performance','performance','quality','quality','quality','quality', 'comfort','comfort','comfort','comfort','reliability','reliability','reliability','reliability','styling','styling','styling','styling','comments','comments','comments','comments','comments','comments'],
           ['model','amount','carmax.com','kbb.com','cars.com','average','carmax.com','kbb.com','cars.com','average','carmax.com','kbb.com', 'cars.com','average','carmax.com','kbb.com','cars.com','average','carmax.com','kbb.com','cars.com','average','carmax.com','kbb.com','cars.com','average','carmax.com','kbb.com','cars.com','average','carmax.com','kbb.com','cars.com','carmax.com','kbb.com','cars.com']
           
          ]
column_tuples = list(zip(*columns))
index = pd.MultiIndex.from_tuples(column_tuples, names=["first", "second", 'third'])
df = pd.DataFrame(columns = index, index=[np.arange(0,25)])
df = df.append(pd.Series(), ignore_index=True)

#Set Pandas Display to see all output; mainly used for debugging
pd.set_option('display.max_columns', 300)
pd.set_option('display.max_rows', 300)

"""**Using Selenium and BS on CarMax.com**"""
idx = 0
for i in range(0, len(inspected_cars)):
  cars = {}
  price = []
  
  brand = inspected_cars.iloc[i]['Brand']
  brand = brand.lower()
  model = inspected_cars.iloc[i]['Model']
  model = model.lower()
  year = inspected_cars.iloc[i]['Year']
  print(brand, model, year)
 
  car_review_url = URL2 + "reviews/{}/{}/{}".format(brand,model,year)
  #some information are missing from carmax so we have to accomodate by search for the same car in another year or ignore the car if no reviews are present
  if model == "sentra" or model == "jetta" or model == "passat":
    car_review_url = URL2 + "reviews/{}/{}/{}".format(brand, model, 2019)
  if model == "k5":
    idx += 1
    cars_lst_missing_info[str(year) + brand + model] = "reviews"
    continue
  print(car_review_url)
  #can use requests here, but we are trying Selenium and see how it works
  #headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'}
  #content = requests.get(car_review_url, headers=headers)
  driver = webdriver.Chrome(DRIVER_PATH, options=options)
  driver.get(car_review_url)
  #time.sleep(randint(1,2)) --> for crawl-delay when needed
  content = driver.page_source
  soup = BeautifulSoup(content, "html.parser") 


  results = soup.find(id="customer-reviews")

  car_reviews = results.find(class_="section-2")
  car_reviews_top = car_reviews.find(class_ = "top-likes")
  car_reviews_comments = car_reviews_top.find_all("p")
  car_reviews_ratings = car_reviews.find(class_ = "kmx-typography--display-3").text
  df.at[idx,('rating','consumer','carmax.com')] = car_reviews_ratings[:3]
  
  idx2 = 0
  for car_review in car_reviews_comments:
    if idx2 == 0:
      df.at[idx, ('pros', 'comments', 'carmax.com')] =  "".join(car_review.text)
      idx2 += 1
    else:
      df.at[idx, ('cons', 'comments', 'carmax.com')] = "".join(car_review.text)
  
  #print(df)
  idx += 1
  #print(df)
  
  driver.close()
  sleep(randint(1,2))

"""BS + requests on Cars.com"""
idx = 0

for i in range(0, len(inspected_cars)):
  
  brand = inspected_cars.iloc[i]['Brand']
  brand = brand.lower().replace(' ','')
  model = inspected_cars.iloc[i]['Model']
  model = model.lower().replace(' ','')
  year = inspected_cars.iloc[i]['Year']
  print(brand, model, year)
  if model.lower() == "es":
    model += "_350"
  if model.lower() == "3-series":
    model = "m340"
  if model.lower() == "5-series":
     model = "530"

  car_url = URL4 + 'research/' + brand + '-' + model + '-' + str(year) + '/'
  print(car_url)
  headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'}
  content = requests.get(car_url, headers=headers)
  #sleep(randint(1,2))
  soup = BeautifulSoup(content.content, "html.parser") 
  

  results = soup.find(class_ ="research-mmy-page")
  car_reviews = results.find_all(class_="sds-list sds-list--unordered pros-cons-list")
  car_ratings = results.find(class_="sds-rating__count")
  car_attributes = soup.find(class_= "sds-definition-list review-breakdown--list")
  #print(car_attributes)
  attribute_features = car_attributes.find_all("span")

  df.at[idx,('rating','comfort','cars.com')] = attribute_features[1].text
  df.at[idx,('rating','quality','cars.com')] = attribute_features[3].text
  df.at[idx,('rating','performance','cars.com')] = attribute_features[5].text
  df.at[idx,('rating','styling','cars.com')] = attribute_features[7].text
  df.at[idx,('rating','value','cars.com')] = attribute_features[9].text
  df.at[idx,('rating','reliability','cars.com')] = attribute_features[11].text
      
  #for car pros/cons
  idx2 = 0
  for car_review in car_reviews:
      comments = car_review.find_all("li")
      #print(type(comments))
      comment_combined = ''
      for comment in comments:
        #print(comment.get_text())
        comment_combined += (comment.get_text() + "; ")

      #print("combined: " + comment_combined)
      if idx2 == 0:
        df.at[idx,('pros','comments','cars.com')]  = comment_combined
        idx2 += 1
      else:
        df.at[idx,('cons','comments','cars.com')]  = comment_combined

  #for car ratings expert/consumer
  
  for rating in car_ratings:
    df.at[idx,('rating','consumer','cars.com')] = rating.get_text()

  car_names = results.find("h1").text

  df.at[idx,('car','brand','model')] = "".join(car_names)
  
  idx += 1
  sleep(randint(1,2))

"""**BS + requests on Kbb.com**"""
idx = 0
for i in range(0, len(inspected_cars)):
  dict2 = {}
  brand = inspected_cars.iloc[i]['Brand']
  brand = brand.lower()
  model = inspected_cars.iloc[i]['Model']
  model = model.lower()
  year = inspected_cars.iloc[i]['Year']
  print(brand, model, year)
  car_url = URL1 + brand.replace(" ","")+ '/' + model.replace(" ","") + '/' + str(year) + '/'
  print(car_url)
  headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'}
  content = requests.get(car_url, headers=headers)
  soup = BeautifulSoup(content.content, "html.parser") 

  results = soup.find(id ="expertreview")
  car_reviews = results.find_all(class_="css-180tk1l-ColBase")
  car_ratings = soup.find_all(class_="css-1a75k9o")[:2]
  car_attributes = soup.find_all(class_= "css-v687s9-ColBase eib3s4b0")

  for car_attribute in car_attributes:
      attribute_name = car_attribute.find(class_ = "css-18hufr0").text
      attribute_rating = car_attribute.find(class_="css-1disuz8-ShortHandBarRating").text

      df.at[idx,('rating',attribute_name.lower().replace(" ",""),'kbb.com')] = attribute_rating

  #for car pros/cons
  idx2 = 0
  for car_review in car_reviews:
      comments = car_review.find_all("li")

      if not comments:
          comments = car_review.find_all("p")
      
      #sleep(randint(1,2))
      comment_combined = ''
      for comment in comments:
        
        comment_combined += (comment.get_text() + '; ')


      if idx2 == 0:
        df.at[idx,('pros','comments','kbb.com')] = comment_combined
        idx2 += 1
      else:
        df.at[idx,('cons','comments','kbb.com')] = comment_combined

  #for car ratings expert/consumer
  idx2 = 0
  for rating in car_ratings:
      if idx2 == 0:
        idx2 += 1
      else:
        df.at[idx,('rating','consumer','kbb.com')] = rating.text;
          

  car_names = results.find("h2")

  df.at[idx,('car','brand','model')] = "".join(car_names)[:-6]
        
  #print(df)
    
  idx += 1
  sleep(randint(1,2))
print(cars_lst_missing_info.items())

"""organize dataframe and find average of all ratings from websites"""
for i in np.arange(0,len(inspected_cars)):
  print(str(df.at[i,('car','brand','model')]).lower())
  if str(df.at[i,('car','brand','model')]).lower().replace(" ","") in cars_lst_missing_info.keys():
      df.at[i,('rating','consumer','average')] = (np.double(df.at[i,('rating','consumer','kbb.com')])+ np.double(df.at[i,('rating','consumer','cars.com')])) / 2.0
  else:
      df.at[i,('rating','consumer','average')] = (np.double(df.at[i,('rating','consumer','carmax.com')])+ np.double(df.at[i,('rating','consumer','kbb.com')]) + np.double(df.at[i,('rating','consumer','cars.com')])) / 3.0
  df.at[i,('rating','value','average')] = (np.double(df.at[i,('rating','value','kbb.com')]) + np.double(df.at[i,('rating','value','cars.com')])) / 2.0
  df.at[i,('rating','performance','average')] = (np.double(df.at[i,('rating','performance','kbb.com')])+np.double(df.at[i,('rating','performance','cars.com')])) / 2.0
  df.at[i,('rating','quality','average')] = (np.double(df.at[i,('rating','quality','kbb.com')])+np.double(df.at[i,('rating','quality','cars.com')])) / 2.0
  df.at[i,('rating','comfort','average')] = (np.double(df.at[i,('rating','comfort','kbb.com')])+np.double(df.at[i,('rating','comfort','cars.com')])) / 2.0
  df.at[i,('rating','reliability','average')] = (np.double(df.at[i,('rating','reliability','kbb.com')])+np.double(df.at[i,('rating','reliability','cars.com')])) /2.0
  df.at[i,('rating','styling','average')] = (np.double(df.at[i,('rating','styling','kbb.com')])+np.double(df.at[i,('rating','styling','cars.com')])) / 2.0

  df.at[i,('car','price','amount')] = inspected_cars.iloc[i]['Price(manufacturer)']

with open('cars.csv', mode='w', newline='\n') as f:
  df.to_csv(f,index=False, encoding='utf-8')


      
quit()