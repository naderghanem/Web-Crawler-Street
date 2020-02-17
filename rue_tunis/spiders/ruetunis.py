# -*- coding: utf-8 -*-
import scrapy
from scrapy import Spider
from scrapy.http import Request, FormRequest
import pandas as pd

class RuetunisSpider(scrapy.Spider):
	name = 'ruetunis'
	allowed_domains = ['rues-tunisie.openalfa.com']
	start_urls = ['http://rues-tunisie.openalfa.com/']

	# Global variables initialization
	final_street_name = []
	final_street_type = []

	

	def parse(self, response):
		# Our base Url
		start_url = 'https://rues-tunisie.openalfa.com/tunis/liste-rues'
		# Liste of the first letter of the streets
		alfa_list = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","Y","0-9"]
		# fetching the website links
		for alfa in alfa_list:
			url_first = start_url + "/" + alfa
			yield Request(url_first, callback=self.Next_page)

		# Site pagination 
	def Next_page(self, response):
		current_url = response.url
		if response.xpath("""//*[@class="wp-pagenavi"]""")!=[]:
			# Getting the link
			page_num_link = response.xpath("""//*[@class="wp-pagenavi"]/a[last()]/@href""").extract_first()
			# separate the link to get the page number and put it in a varaible
			page_num =page_num_link.split("=")
			for i in range(1, int(page_num[1])+1):
				url_next = current_url + "?pg=" + str(i)
				yield Request(url_next, callback=self.parse_street)
		else:
			yield Request(current_url, callback=self.parse_street)



	def parse_street(self, response):

		# Define the global variable 
		global final_street_name
		global final_street_type

		# Extracte the street names and types by Xpath
		List_street_name = response.xpath("""//*[@id="divcalles"]/div/ul/li/div[1]/text()""").extract()
		List_street_type = response.xpath("""//*[@id="divcalles"]/div/ul/li/div[2]/text()""").extract()


		# Update the street lists
		for i in range(0, len(List_street_name)):
			self.final_street_name.append(List_street_name[i])
			self.final_street_type.append(List_street_type[i])

		

		# Creat the street table using Panda library 
		Table = pd.DataFrame({
			'Street name':self.final_street_name,
			'Street type':self.final_street_type
			},
			columns=['Street name','Street type']) 
		self.to_excel_save(Table,'rues_tunis.csv')


	def to_excel_save(self,Table,Name_file):
		# Using Panda library to write in the excel file
		final= pd.DataFrame(Table)       
		final.to_csv('rues_tunis.csv')
