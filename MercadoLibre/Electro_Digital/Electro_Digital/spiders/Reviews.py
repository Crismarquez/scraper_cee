# -*- coding: utf-8 -*-
"""
Created on Sat May 30 12:54:43 2020

@author: Cristian Marquez
"""


# import scrapy
# import re
# from datetime import datetime
# from unidecode import unidecode
# import pandas as pd

# class MercadoLibreSpider(scrapy.Spider):
#     name = 'MercadoLibreFerreteria'
#     allowed_domains = ['mercadolibre.com.co']
    
#     path = "C:/Users/Cristian Marquez/Documents/Cristian/Academico/Modelacion y ciencia computacional/100. tesis/Proyecto/"
#     crawler = "Electro_Digital/Electro_Digital/spiders/"
#     file= "Bot_Mercadolibre.csv"
    
#     df = pd.read_csv((path+crawler+file), usecols=['Url_Comentarios'])
#     df = df.dropna(axis=0)
    
#     start_urls = df.Url_Comentarios.values.tolist()

#     def cleandata(self,string):
#         if not string:
#             string=""
#         string = string.rstrip()
#         string = string.strip()
#         string = unidecode(string)
#         string = string.replace("\n"," ")
#         string = re.sub('[,Â()\t=*|_.-><]', '', string)
#         return string.lower()
        
#     def parse(self, response):
#         item_id = response.xpath('//input[@name="itemIdValue"]/@value').extract_first() 
#         product_id = response.xpath('//input[@name="productIdValue"]/@value').extract_first() 
#         total_reviews = response.xpath('//input[@name="totalReviews"]/@value').extract_first() 
        
#         part_a = 'https://articulo.mercadolibre.com.co/noindex/catalog/reviews/search?'
#         part_b = '&modal=true&offset=0&limit='
#         part_c = '&totalReviews='
        
#         if product_id:
#             p_id = 'productId='+product_id+'&'
#             url_total_reviews = part_a + p_id + 'itemId=' + item_id + part_b + total_reviews + part_c
        
#         else:
#             url_total_reviews = part_a + 'itemId=' + item_id + part_b + total_reviews + part_c

             
#         yield scrapy.Request(url_total_reviews, callback = self.parse_reviews,
#                                  meta={'item_id': item_id, 'total_reviews': total_reviews})
        
#     def parse_reviews(self, response):
#         now = datetime.now()
#         fecha =now.strftime('%Y/%m/%d')
        
#         item_id = response.meta['item_id']
#         total_reviews = response.meta['total_reviews']
        
#         reviews = response.xpath('//article[@class="review-element"]')
#         for review in reviews:
#             stars = len(review.xpath('.//div[@class="review-stars"]//stop[@offset="100%"]'))  
#             title = self.cleandata(review.xpath('.//label/text()').extract_first())
#             comment = [self.cleandata(review.xpath('.//p/text()').extract_first())]
            
#             yield {'Fecha':fecha,
#                    'Hora':now.hour,
#                    'Almacen':"Mercado Libre",
#                    'Item_id': item_id,
#                    'Title': title,
#                    'Comment': comment,
#                    'Stars': stars,
#                    'Total_reviews': total_reviews}