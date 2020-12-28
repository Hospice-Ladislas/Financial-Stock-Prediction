#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script scrapes data from stock website
"""
## Packages download
from selenium import webdriver
import pandas as pd
from datetime import datetime,timedelta
from itertools import product


driver = webdriver.Chrome('./chromedriver 2')

URL = 'http://abourse.com/histoActionsJour.html'

driver.get(URL)



def availabilityOfData(date):
    
    """
    The goal of this function is to check if data is available for this date.
    0 when data is not available and 1 if it is
    """
    
    checkdata = driver.find_element_by_id("date")
    checkdata.clear()
    checkdata.send_keys(date)
    checkdata.submit()
    
    verif = driver.find_element_by_xpath("/html/body/div/div[3]/div[1]/div[2]/div[4]").text.split(" ")

    if "trouvée!" in verif:
        return 0
    else:
        return 1
    
  
def modify_list(list_name):
    
    output = [val for sublist in list_name for val in sublist]
    return output

def outputToDataFrame(lst, n, date_list):
    
    """
    
    This function transforms list of data to dataframe

    """
    columns_name = ["Symbole","Titre","Cotation_Volume","Cotation_Valeur","Cours_Precedent",
                    "Cours_Ouv","Cours_Clot","Cours_Moy","Variation","Variation_Ann_Prec",
                    "Cours_Reference","Ecarts_Maximaux_Bas","Ecarts_Maximaux_Haut",
                    "Dernier_Dividende_Montant_Net","Dernier_Dividende_Date","Comp","Rdt_Net","PER"]
    list_modif, date_list_modif = modify_list(lst), modify_list(date_list)  
    
    sub=[] ; result=[]
    for i in list_modif:
        sub+=[i]
        if len(sub)==n: result+=[sub] ; sub=[]
    if sub: result+=[sub]
    
    data = pd.DataFrame(result,columns=columns_name)
    date_data = pd.DataFrame(date_list_modif,columns=["Date"])
    
    output = pd.concat([date_data,data], axis=1)

    return output
    
def getData(listOfdays):
    
    """
    This function consists to collect data from website.
    
    It returns data as list and the list of dates which we collect data

    """
    
    result, lst_date = [], []
    for date in listOfdays:
    
        if availabilityOfData(date)==1:
            
            basepath = "/html/body/div/div[3]/div[1]/div[2]/div[4]/div/div/table/tbody[2]"
            allDataOfPage = driver.find_element_by_xpath(basepath).text.split("\n")
            
            usefulIndex = [index+1 for index,allData in enumerate(allDataOfPage) if len(allData.split(" "))>15]
            
            result.append([driver.find_element_by_xpath(basepath+"/tr["+str(i)+"]/td["+str(j)+"]").text 
                    for i,j in product(usefulIndex,range(1,19))])
            
            lst_date.append([date for i in range(len(usefulIndex))])

            
    return result, lst_date



def getWorkdays(start, end, excluded=(6, 7)):
    
    """
    This function takes start and end for interval period to keep only weekdays.
    
    Because, we don't have data in weekends

    """
    
    start, end = datetime.strptime(start,"%Y-%m-%d"), datetime.strptime(end,"%Y-%m-%d")
    days = []
    
    while start.date() <= end.date():
        if start.isoweekday() not in excluded:
            days.append(start)
        start += timedelta(days=1)
    days_final = [jour.strftime("%Y-%m-%d") for jour in days]
    return days_final

if __name__== "__main__":
    list_date = getWorkdays("2016-08-09","2016-08-10")
    data, lst_date = getData(list_date)
    dataFinal = outputToDataFrame(data, 18,lst_date)
    dataFinal.to_csv("data/StockData_part1.csv",index=False)




