# -*- coding: utf-8 -*-
"""
Created on Wed Dec 25 19:41:37 2019

@author: Cristian Marquez
"""

import scrapy
import re
from datetime import datetime
from unidecode import unidecode


class JumbocelSpider(scrapy.Spider):
    name = 'JumboCel4'
    allowed_domains = ['tiendasjumbo.co']
    start_urls = ['https://www.tiendasjumbo.co/buscapagina?sl=49a31962-b0e8-431b-a189-2473c95aeeeb&PS=30&cc=18&sm=0&PageNumber=1&&fq=C%3a%2f47%2f63%2f2000117%2f&O=OrderByTopSaleDESC']
    
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
        productos=response.xpath('//li[@class="tienda-de-tecnologia-online-con-lo-ultimo-|-jumbo-colombia"]')
        
        for producto in productos:
            url=producto.xpath('.//div[@class="product-item__info"]/a/@href').extract_first()
            pnormal=producto.xpath('.//span[@class="product-prices__value"]/text()').extract_first()
            phoy= producto.xpath('.//span[@class="product-prices__value product-prices__value--best-price"]/text()').extract_first()

            yield scrapy.Request(url,
                                callback=self.productos,
                                meta={'url':url,'pnormal':pnormal,'phoy':phoy}
                                )
        npag=1
        url1='https://www.tiendasjumbo.co/buscapagina?sl=49a31962-b0e8-431b-a189-2473c95aeeeb&PS=30&cc=18&sm=0&PageNumber='
        for i in range (30):
                npag=npag+1
                url2='&&fq=C%3a%2f47%2f63%2f2000117%2f&O=OrderByTopSaleDESC'
                siguiente_pag = url1 + str(npag)+ url2
                yield scrapy.Request(siguiente_pag,callback=self.continuar)
                
    def continuar(self, response):
        productos=response.xpath('//li[@class="tienda-de-tecnologia-online-con-lo-ultimo-|-jumbo-colombia"]')
        
        for producto in productos:
            url=producto.xpath('.//div[@class="product-item__info"]/a/@href').extract_first()
            pnormal=producto.xpath('.//span[@class="product-prices__value"]/text()').extract_first()
            phoy= producto.xpath('.//span[@class="product-prices__value product-prices__value--best-price"]/text()').extract_first()
            
            yield scrapy.Request(url,callback=self.productos,
                                 meta={'url':url,
                                       'pnormal':pnormal,
                                       'phoy':phoy})

        
    def productos(self, response):
        url=response.meta['url'] 
        nombre=response.xpath('//div[@class="name"]/h1/div/text()').extract_first()
        description = response.xpath('//div[@class="productDescription"]/text()').extract_first() 
        pnormal=response.meta['pnormal']
        phoy=response.meta['phoy']
        ptarjeta=response.xpath('.//div[@class="plugin-preco"]/p/div/span[@class="product-prices__value"]/text()').extract_first()
        marca=response.xpath('.//span[@class="brand"]//text()').extract_first()
        referencia=response.xpath('.//*[contains(text(), "Modelo")]/following-sibling::*[1]/text()').extract_first()
        if not referencia:
            referencia=response.xpath('.//*[contains(text(), "REFERENCIA")]/following-sibling::*[1]/text()').extract_first()
       
        almacenamiento=response.xpath('.//*[contains(text(), "Memoria interna")]/following-sibling::*[1]/text()').extract_first()
        mram=response.xpath('.//*[contains(text(), "MEMORIA RAM")]/following-sibling::*[1]/text()').extract_first()
        color=response.xpath('.//*[contains(text(), "COLOR PRINCIPAL")]/following-sibling::*[1]/text()').extract_first()
        sku=str(response.xpath('.//div[@class="skuReference"]/text()').extract_first())
        ean=str(response.xpath('.//*[contains(text(), "EAN")]/following-sibling::*[1]/text()').extract_first())
        if ean == "None":
            a=response.xpath('.//*[contains(text(), "Eans")]/text()').extract_first()
            p=a.find('Eans":["')
            ean=str(a[p+7:p+21])
        now = datetime.now()
        fecha =now.strftime('%Y/%m/%d')
        referencia=response.xpath('.//*[contains(text(), "Modelo")]/following-sibling::*[1]/text()').extract_first()
        
        subcas = response.xpath('//div[@class= "bread-crumb"]/ul//span[@itemprop="name"]/text()').extract()
        subca1 = subcas[2]
        try:
            subca2 = subcas[3]
        except:
            subca2 = subca1
            
        
        if not nombre:
            nombre=""
        if not pnormal:
            pnormal=""
        if not phoy:
            phoy=""
        if not ptarjeta:
            ptarjeta=""
        if not marca:
            marca=""
        if not referencia:
            referencia=""
        if not almacenamiento:
            almacenamiento=""
        if not mram:
            mram=""
        if not color:
            color=""
        if not sku:
            sku=""


        pnormal= re.sub('[$ Â.\n\r]', '', pnormal)
        pnormal=pnormal.replace(u'\xa0','')
        phoy=phoy.replace(u'\xa0','')
        phoy= re.sub('[$ Â.\n\r]', '', phoy)   
        phoy=phoy.replace(',','.')
        ptarjeta= re.sub('[$ Â.\n\r]', '', ptarjeta)
        ptarjeta=ptarjeta.replace(u'\xa0','')
        

        
        yield {'Fecha':fecha,
               'Hora':now.hour,
               'Almacen':"Jumbo",
               'Categoria':"Telefonia",
               'Sub_categoria1':self.cleandata(subca1),
               'Sub_categoria2':self.cleandata(subca2),
               'Nombre':self.cleandata(nombre),
               'Description': self.cleandata(description),
               'Sku':sku,
               'Ean':ean,
               'Url':url,
               'Modelo':referencia,
               'Marca':self.cleandata(marca),
               'Precio_hoy':phoy
               } 