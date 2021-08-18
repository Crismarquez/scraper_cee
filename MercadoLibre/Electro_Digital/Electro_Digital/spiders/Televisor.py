# -*- coding: utf-8 -*-
"""
Created on Sat May 30 12:54:43 2020

@author: Cristian Marquez
"""


import scrapy
import re
from datetime import datetime
from unidecode import unidecode

class MercadoLibreSpider(scrapy.Spider):
    name = 'MercadoLibreAudioVideo1'
    allowed_domains = ['mercadolibre.com.co']
    start_urls = ['https://electronica.mercadolibre.com.co/televisores/nuevo/',
                  'https://electronica.mercadolibre.com.co/convertidores-a-smart-tv/nuevo/']

    # 'https://computacion.mercadolibre.com.co/tablets-accesorios/nuevo/
    def cleandata(self,string):
        if not string:
            string=""
        string = string.strip()
        string = unidecode(string)
        string = re.sub('[,Â()\t=*|_.-]', '', string)
        string = string.replace("\n","")
        string = string.replace("\r","")  
        return string.lower()

         
    def parse(self,response):
        productos=response.xpath('//li[contains(@class, "results-item")]')  
        
        if not productos:
            productos = response.xpath('//li[contains(@class, "layout__item")]') 
            
            for producto in productos:
                url = producto.xpath('.//div[contains(@class,"item__group--title")]/a/@href').extract_first()
                if url.find('_JM') != -1:
                    url = url[:url.find('_JM')+3]
                    yield scrapy.Request(url, callback = self.parse_publicado,
                                         meta={'url': url})
                
        else:
            for producto in productos:
                url = producto.xpath('.//div/h2/a/@href').extract_first()
                if url.find('_JM') != -1:
                    url = url[:url.find('_JM')+3]
                    yield scrapy.Request(url, callback = self.parse_publicado,
                                         meta={'url': url})

        cont_next = response.xpath('//li[contains(@class, "andes-pagination__button--next")]')     
        next_page = cont_next.xpath('.//a/@href').extract_first()
        try:
            n_page = next_page[-6:]
            n_page = int(re.sub('\D','',n_page))
        except:
            n_page = 0
        
        max_item = 3000
        if n_page < max_item: 
            yield scrapy.Request(next_page,
                                  callback = self.parse)
                
    def parse_publicado(self,response):
        url=response.meta['url']
        
        nombre=response.xpath('//header[@class="item-title"]/h1/text()').extract_first()
        if not nombre:
            nombre = response.xpath('//h1[@class="ui-pdp-title"]/text()').extract_first()
            item_id = response.xpath("//input[@name='itemId']/@value").extract_first()  
            pnormal = response.xpath('//span[@class="price-tag-fraction"]/text()').extract_first()
            description = response.xpath('//p[@class="ui-pdp-description__content"]/text()').extract() 
            description = " ".join(description)
            subcas = response.xpath('//ul[@class="andes-breadcrumb"]/li/a[contains(@class, "breadcrumb")]/text()').extract() 
            
            if subcas:
                subca1 = subcas[1]   
            else:
                subca1 = ""
                
            try:
                subca2 = subcas[2]
            except:
                subca2 = subca1
            
            marca = response.xpath('//th[contains(text(),"Marca")]/following-sibling::*[1]//text()').extract_first()  
            referencia = response.xpath('//th[contains(text(),"Modelo")]/following-sibling::*[1]//text()').extract_first()  
            vendidos = response.xpath('//span[@class="ui-pdp-subtitle"]/text()').extract_first()
            comentarios = response.xpath('//span[@class="ui-pdp-review__amount"]/text()').extract_first() 
            if comentarios:
                comentarios = re.sub('\D', "", comentarios)
            url_comentarios = response.xpath('//div[@class="andes-tabs-content ui-pdp-reviews__comments__tab-content"]/a/@href').extract_first()
            interacciones=""
            calificacion = len(response.xpath('//svg[@class="ui-pdp-icon ui-pdp-icon--star-full"]').extract())
            tienda = response.xpath('//h3[@class="ui-pdp-seller__header__title"]/text()').extract_first() 
            url_interacciones = response.xpath('//div[contains(@class, "ui-pdp-questions__questions-others-question-modal")]/div[@class="ui-pdp-action-modal"]/a/@href').extract_first()
            
        else:
            nombre=response.xpath('//header[@class="item-title"]/h1/text()').extract_first().strip()
            item_id = response.xpath("//input[@name='itemId']/@value").extract_first()  
            pnormal = response.xpath('//span[@class="price-tag"]/span[2]/text()').extract_first()        
            description = response.xpath('//div[@class="item-description__text"]/p/text()').extract()
            description = " ".join(description)
            
            subcas = response.xpath('//ul[@class="vip-navigation-breadcrumb-list"]/li/a[contains(@class, "breadcrumb")]/text()').extract()
            subca1 = subcas[1]
            
            try:
                subca2 = subcas[2]
            except:
                subca2 = subca1
            
            marca=response.xpath('//strong[contains(text(),"Marca")]/following-sibling::*[1]/text()').extract_first()
            referencia=response.xpath('//div[@class="specs-wrapper"]//li/strong[contains(text(), "Modelo")]/following-sibling::*[1]/text()').extract_first()
            vendidos=response.xpath('//div[@class="item-conditions"]').extract_first()
            comentarios=response.xpath('//span[@class="average-legend"]/span/text()').extract_first() 
            url_comentarios=response.xpath('//section[@id="reviewsCard"]/a/@href').extract_first()
            calificacion=response.xpath('//div[@class="vip-card"]/div[@class="card-section"]/span[@class="review-summary-average"]/text()').extract_first()
            tienda=response.xpath('//div[@class="official-store-info"]/p[@class="title"]/text()').extract_first() 
            url_interacciones = response.xpath('//section[@id = "vip-section-question"]/a/@href').extract_first()
     
        now = datetime.now()
        fecha =now.strftime('%Y/%m/%d')
        
        if url_comentarios:
            url_comentarios='https://articulo.mercadolibre.com.co'+ url_comentarios
        if url_interacciones:
            url_interacciones='https://articulo.mercadolibre.com.co'+ url_interacciones
        
        if not pnormal:
            pnormal=""
        if not vendidos:
            vendidos="no-data"
            
        try:
            url = url[:url.find('_JM')+3]
        except:
            pass
        try:
            url_interacciones = url_interacciones[:url_interacciones.find('?')+1]
        except:
            pass
        
        phoy=pnormal
        phoy = re.sub('[$ Â.\n\r]', '', phoy)
        phoy = phoy.replace(u'\xa0','')
        vendidos = re.findall(r'\d+', vendidos)
#        tienda = self.cleandata(tienda)

        subcas_com = ['', '', '', '', '']
        if len(subcas)>5:
            subcas = subcas[:5]
            
        for i in range(len(subcas)):
            subcas_com[i] = subcas[i]

        yield {'Fecha':fecha,
               'Almacen':"Mercado Libre",
               'Categoria':'Audio y video',
               'Sub_categoria1':self.cleandata(subcas_com[0]),
               'Sub_categoria2':self.cleandata(subcas_com[1]),
               'Sub_categoria3':self.cleandata(subcas_com[2]),
               'Sub_categoria4':self.cleandata(subcas_com[3]),
               'Sub_categoria5':self.cleandata(subcas_com[4]),
               'Nombre':self.cleandata(nombre),
               'Marca': self.cleandata(marca),
               'Referencia': self.cleandata(referencia),
               'Url':url,
               'Item_id': item_id,
               'Url_Comentarios':url_comentarios,   
               'Url_Interacciones':url_interacciones,
               'Precio_hoy':phoy,               
               'Vendidos':vendidos,
               'Tienda':tienda,
               'Comentarios':comentarios,
               'Calificacion':calificacion
               }  