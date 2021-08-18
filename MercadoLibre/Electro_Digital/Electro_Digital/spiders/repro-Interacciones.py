# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 16:05:15 2020

@author: Cristian Marquez
"""
import scrapy
import re
from datetime import datetime
from unidecode import unidecode
import pandas as pd

class MercadoLibreSpider(scrapy.Spider):
    name = 'MercadoLibreInteracciones'
    allowed_domains = ['mercadolibre.com.co']
    

    
    #start_urls = df.Url_Interacciones.values.tolist()[:1000]
    start_urls = ['https://articulo.mercadolibre.com.co/noindex/questions/MCO513556181?scroll_to_question=10&new_version=true']

    def cleandata(self,string):
        if not string:
            string=""
        string = string.rstrip()
        string = string.strip()
        string = unidecode(string)
        string = string.replace("\n"," ")
        string = re.sub('[,Â()\t=*|_.-]', '', string)
        return string.lower()
        
    def parse(self, response):
        
        path = "C:/Users/Cristian Marquez/Documents/Cristian/Academico/Modelacion y ciencia computacional/100. tesis/Proyecto/"
        crawler = "Electro_Digital/Electro_Digital/spiders/"
        file= "Bot_MercadoLibre.csv"
        
        df = pd.read_csv((path+crawler+file), usecols=['Url_Interacciones','Fecha'])
        now = datetime.now()
        hoy=now.strftime('%Y/%m/%d')

        df =df[df['Fecha']==hoy]
        df = df.drop_duplicates()
        df = df.dropna(axis=0)
        
        urls_obj = df.Url_Interacciones.values.tolist()
        
        path = "C:/Users/Cristian Marquez/Documents/Cristian/Academico/Modelacion y ciencia computacional/100. tesis/Proyecto/"
        crawler = "Electro_Digital/Electro_Digital/spiders/"
        file= "Interacciones.csv"
        
        df = pd.read_csv((path+crawler+file), usecols=['Url_Interacciones'])
        df = df.drop_duplicates()
        
        urls_rastr = df.Url_Interacciones.values.tolist()
        
        validar = []
        for url in urls_obj:
            if url not in urls_rastr:
                validar.append(url)
        
        
        for url in validar:
            yield scrapy.Request(url, callback = self.parse_interaccion)
        
        
        
        
    def parse_interaccion(self, response):
        
        Url_Interacciones = str(response)
        Url_Interacciones = Url_Interacciones.replace('<200 ', "")
        Url_Interacciones = Url_Interacciones.replace('>', "")
        
        
        questions = response.xpath('//ul[@class="questions__list"]/li/article[contains(@class, "questions__item--question")]/div[@class="questions__content"]/p/text()').extract()
        
        if not questions:
            questions = response.xpath('//div[@class="ui-pdp-questions__questions-list"]/div/div/div[1]/span/text()').extract()
            
        now = datetime.now()
        fecha =now.strftime('%Y/%m/%d')
        
        if Url_Interacciones.find('?') != -1:
            Url_Interacciones = Url_Interacciones[:Url_Interacciones.find('?')+1]
        else :
            Url_Interacciones = Url_Interacciones + '?'


        for question in questions:

            yield {'Fecha':fecha,
                    'Hora':now.hour,
                    'Almacen':"Mercado Libre",
                    'Url_Interacciones': Url_Interacciones,
                    'Question': self.cleandata(question)
                    }