# -*- coding: utf-8 -*-
"""
Created on Wed Dec 25 19:41:37 2019

@author: Cristian Marquez
"""

import scrapy
import re
from datetime import datetime
from unidecode import unidecode


class JumbocelSpiderElecH(scrapy.Spider):
    name = 'JumboElecH'
    allowed_domains = ['tiendasjumbo.co']
    start_urls = ['https://www.tiendasjumbo.co/buscapagina?sl=49a31962-b0e8-431b-a189-2473c95aeeeb&PS=18&cc=18&sm=0&PageNumber=1&&fq=C%3a%2f1%2f&O=OrderByTopSaleDESC']
    
    
    def parse(self, response):
        productos=response.xpath('//li[@class="venta-de-electrodomesticos-de-las-mejores-marcas-|-jumbo-colombia"]')
        
        for producto in productos:
            url=producto.xpath('.//div[@class="product-item__info"]/a/@href').extract_first()
            pnormal=producto.xpath('.//span[@class="product-prices__value"]/text()').extract_first()
            phoy= producto.xpath('.//span[@class="product-prices__value product-prices__value--best-price"]/text()').extract_first()

            yield scrapy.Request(url,
                                callback=self.productos,
                                meta={'url':url,'pnormal':pnormal,'phoy':phoy}
                                )
        npag=1
        url1='https://www.tiendasjumbo.co/buscapagina?sl=49a31962-b0e8-431b-a189-2473c95aeeeb&PS=18&cc=18&sm=0&PageNumber='
        for i in range (30):
                npag=npag+1
                url2='&&fq=C%3a%2f1%2f&O=OrderByTopSaleDESC'
                siguiente_pag = url1 + str(npag)+ url2
                yield scrapy.Request(siguiente_pag,callback=self.continuar)
                
    def continuar(self, response):
        productos=response.xpath('//li[@class="venta-de-electrodomesticos-de-las-mejores-marcas-|-jumbo-colombia"]')
        
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
        pnormal=response.meta['pnormal']
        phoy=response.meta['phoy']
        ptarjeta=response.xpath('.//div[@class="plugin-preco"]/p/div/span[@class="product-prices__value"]/text()').extract_first()
        sku=str(response.xpath('.//div[@class="skuReference"]/text()').extract_first())
        ean=str(response.xpath('.//*[contains(text(), "EAN")]/following-sibling::*[1]/text()').extract_first())
        if ean == "None":
            a=response.xpath('.//*[contains(text(), "Eans")]/text()').extract_first()
            p=a.find('Eans":["')
            ean=str(a[p+7:p+21])
        now = datetime.now()
        fecha =now.strftime('%Y/%m/%d')
        referencia=response.xpath('.//*[contains(text(), "Modelo")]/following-sibling::*[1]/text()').extract_first()
        
        if not nombre:
            nombre=""
        if not pnormal:
            pnormal=""
        if not phoy:
            phoy=""
        if not ptarjeta:
            ptarjeta=""
        if not sku:
            sku=""

            
        # limpiar             
        nombre = re.sub('[,Â]', '', nombre)
        nombre=nombre.replace(u'\xa0','')
        nombre=unidecode(nombre)
        nombre=nombre.lower()
        pnormal= re.sub('[$ Â.\n\r]', '', pnormal)
        pnormal=pnormal.replace(u'\xa0','')
        phoy= re.sub('[$ Â.\n\r]', '', phoy)
        phoy=phoy.replace(u'\xa0','')
        phoy=phoy.replace(',','.')
        ptarjeta= re.sub('[$ Â.\n\r]', '', ptarjeta)
        ptarjeta=ptarjeta.replace(u'\xa0','')
        sku= re.sub('[$ Â. \n \r]', '', sku)
        ean=re.sub('\D','',ean)
        

        
        yield {'Fecha':fecha,
               'Hora':now.hour,
               'Almacen':"Jumbo",
               'Categoria':"Electro Hogar",
               'Nombre':nombre,
               'Sku':sku,
               'Ean':ean,
               'Url':url,
               'Precio_hoy':phoy,
               'Modelo':referencia,
               } 