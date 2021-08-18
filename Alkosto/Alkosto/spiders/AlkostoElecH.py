# -*- coding: utf-8 -*-
import scrapy
import re
from datetime import datetime
from unidecode import unidecode

class AlkostoSpiderElect(scrapy.Spider):
    name = 'alkostoElecH'
    allowed_domains = ['alkosto.com']
    start_urls = ['https://www.alkosto.com/electro']

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
        contenedor=response.xpath('//div[@class = "product__list--wrapper"]')
        productos=contenedor.xpath('.//li[contains(@class, "product__list--item")]')
        
        for producto in productos:
            url=producto.xpath('.//*[@class="product__information"]/h2/a/@href').extract_first()
            url = response.urljoin(url)
            yield scrapy.Request(url, callback = self.parse_publicado,
                                 meta={
                                      'url':url
                                      }
                                 )
        siguiente_pag = response.xpath('//nav[@class="pagination--buttons"]/div[contains(@class, "js-paginationArrowRight")]/a/@href').extract_first()
        url_absoluta=response.urljoin(siguiente_pag)
            
        if siguiente_pag:
            yield scrapy.Request(url_absoluta, callback = self.parse)
                
    def parse_publicado(self,response):
        url = response.meta['url']
        nombre = response.xpath('//div[contains(@class, "product-name")]/h1/text()').extract_first()
        #marca = response.xpath('//table[@id="product-attribute-specs-table"]//th[contains(text(),"MARCA")]/following-sibling::*[1]/text()').extract_first()
        phoy = response.xpath('//div[@class="product-main-info"]//div[contains(@class, "price-block")]//div/input/@value').extract_first()
        now = datetime.now()
        fecha =now.strftime('%Y/%m/%d')
        item_id = response.xpath('//span/span[@class="code"]/text()').extract_first()
        
        subcas = response.xpath('//ol[contains(@class, "breadcrumb")]/li/a/text()').extract()[1:]
        subcas_com = ['', '', '', '', '']
        if len(subcas)>5:
            subcas = subcas[:5]
            
        for i in range(len(subcas)):
            subcas_com[i] = subcas[i]
        
        if not nombre:
            nombre=""

        
        yield {'Fecha':fecha,
               'Almacen':"Mercado Libre",
               'Categoria':'Electro-Hogar',
               'Sub_categoria1':self.cleandata(subcas_com[0]),
               'Sub_categoria2':self.cleandata(subcas_com[1]),
               'Sub_categoria3':self.cleandata(subcas_com[2]),
               'Sub_categoria4':self.cleandata(subcas_com[3]),
               'Sub_categoria5':self.cleandata(subcas_com[4]),
               'Nombre':self.cleandata(nombre),
               'Marca': "",
               'Url':url,
               'Item_id': item_id,
               'Precio_hoy':phoy
               }  
