# -*- coding: utf-8 -*-
"""
Created on Sun Jan 12 10:58:33 2020

@author: Cristian Marquez
"""

import scrapy
import re
from datetime import datetime
from unidecode import unidecode

class LinioSpider(scrapy.Spider):
    name = 'LinioCel'
    allowed_domains = ['linio.com.co']
    start_urls = ['https://www.linio.com.co/c/celulares-y-tablets/celulares-y-smartphones',
                  'https://www.linio.com.co/c/tablets/tablet',
                  'https://www.linio.com.co/c/smartwatches/smartwatch',
                  'https://www.linio.com.co/c/accesorios-para-celulares/audifonos']

    
    def cleandata(self,string):
        if not string:
            string=""
        string = string.strip()
        string = unidecode(string)
        string = re.sub('[,Â()\t=*|_.-]', '', string)
        string = string.replace("\n","")
        string = string.replace("\r","")  
        return string.lower()
    
    def parse(self, response):
        contenedor=response.xpath('//div[contains(@class,"catalogue-product-section")]') 
        urls=contenedor.xpath('.//div[@class="detail-container"]/a/@href').extract()
        
        for i in urls:
            url='https://www.linio.com.co'+i

            
            yield scrapy.Request(url, callback = self.parse_publicado,
                                 meta={
                                      'url':url}
                                 )
        siguiente_pag = response.xpath('//li[@class="page-item"]/a[contains(@class,"page-link")]/@href').extract()
        if len(siguiente_pag) == 2:
            siguiente_pag=siguiente_pag[0]
        else:
            siguiente_pag=siguiente_pag[2]
            
        url_absoluta=response.urljoin(siguiente_pag)    
        if siguiente_pag:
            yield scrapy.Request(url_absoluta, callback = self.parse)
                
    def parse_publicado(self,response):
        url=response.meta['url']
        nombre=response.xpath('//h1/span[@itemprop="name"]/text()').extract_first() 
        description = response.xpath('//div[@itemprop = "description"]//text()').extract()
        description = " ".join(description)
        phoy=response.xpath('//div[@class="product-price"]//span[@class="price-main-md"]/text()').extract_first()
        
        # Ean
        a=response.xpath('.//*[contains(text(), "ean_code")]/text()').extract_first()
        p=a.find('ean_code')
        c=a[p+11:p+28]
        c=c.find(',')
        ean=str(a[p+11:p+c+11])
        if ean.find('-') != -1:
            ean=ean[:ean.find('-')]
        if ean.find('_') != -1:
            ean=ean[:ean.find('_')]
        now = datetime.now()
        fecha =now.strftime('%Y/%m/%d')
        sku=str(response.xpath('//p/span[@class="no-display"]/text()').extract_first())
        
        subcas = response.xpath('//li[@itemprop = "itemListElement"]//span[@itemprop = "name"]/text()').extract()
        subcas = subcas[1:]

        modelo=response.xpath('//div[@class="feature"]/div[contains(text(),"Modelo")]/following-sibling::*[1]/text()').extract_first()
        if modelo:
            modelo.strip()
        
        marca =  response.xpath('//div[@class="product-info-container"]//a[@itemprop="brand"]/text()').extract_first() 
        comentarios = response.xpath('//div[@class="rating-content"]/span[contains(@class,"total-reviews")]/text()').extract_first()
        try:
            comentarios = re.sub('\D','',comentarios)
        except:
            pass
        
        calificacion = response.xpath('//div[@class="rating-content"]/span[@class="star-rating"]/span[contains(@class,"rating-average")]/text()').extract_first()
        if not nombre:
            nombre=""
        if not phoy:
            phoy=""
        
        phoy = re.sub('[$ Â.\n\r]', '', phoy)

        subcas_com = ['', '', '', '', '']
        if len(subcas)>5:
            subcas = subcas[:5]
            
        for i in range(len(subcas)):
            subcas_com[i] = subcas[i]
        
        yield {'Fecha':fecha,
               'Hora':now.hour,
               'Almacen':"Linio",
               'Categoria':"Telefonia",
               'Sub_categoria1':self.cleandata(subcas_com[0]),
               'Sub_categoria2':self.cleandata(subcas_com[1]),
               'Sub_categoria3':self.cleandata(subcas_com[2]),
               'Sub_categoria4':self.cleandata(subcas_com[3]),
               'Sub_categoria5':self.cleandata(subcas_com[4]),
               'Nombre':self.cleandata(nombre),
               'Description': self.cleandata(description),
               'Sku':sku,
               'Ean':ean,
               'Url':url,
               'Precio_hoy':phoy,
               'Referencia':self.cleandata(modelo),
               'Marca': self.cleandata(marca), 
               'Comentarios':comentarios,
               'Calificacion':calificacion}
