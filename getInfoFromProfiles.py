import os, sys
from bs4 import BeautifulSoup
import re
import numpy as np

from selenium import webdriver
from selenium.webdriver.common import action_chains, keys
from selenium.webdriver.common.keys import Keys
from seleniumrequests import Firefox
import time
driver = Firefox()

truckers = np.load("truckers_separated.npy")
truckers = truckers.tolist()

def login_sequence():
	# driver.implicitly_wait(10)
	driver.get("https://illinoisjoblink.illinois.gov")
	# assert 'NBA' in driver.page_source
	action = action_chains.ActionChains(driver)

	# this is the login sequence using the firefox selenium driver
	N = 7  # number of times you want to press TAB
	time.sleep(5)
	action.send_keys(Keys.TAB * N)
	action.send_keys(Keys.RETURN)
	action.send_keys(Keys.TAB)
# 	action.send_keys("") #username for website can be looked up
	action.send_keys(Keys.TAB)
# 	action.send_keys("") #password for website can also be looked up
	action.send_keys(Keys.TAB)
	action.send_keys(Keys.RETURN)
	action.perform()
	# time.sleep(3)

def get_name_number_and_email(html):
	html = html.text
	name = html[html.find('<h1>')+len('<h1>'):html.find('</h1>')]
	name = name.replace("\n"," ")
	html = html[html.find('</head>'):]

	text = BeautifulSoup(html, 'html.parser').get_text()
	email_search = re.search("(\n)(.*)@(.*)(.com|.net|.org)(\s|\n)",text)
	phone_number = re.search("(\d){3}(\D){0,3}(\d){3}(\D){0,3}(\d){4}",text)	

	email = ""

	if email_search != None:
		email = email_search.group(0).replace("\n","")

	if phone_number != None:
		phone_number = phone_number.group(0)
		phone_number = re.split(r"(\D*)", phone_number)
		for el in phone_number:
			if re.compile(r"(\D)").search(el):
				phone_number.remove(el)
		phone_number = "".join(phone_number)
	else:
		phone_number = 'n/a'

	return [name] + [phone_number] + [email]

def cdl_filter(text):
	text = BeautifulSoup(text, 'html.parser').get_text()
	has_cdl = False
	reg1 = r"c[\'\"\.\s]?d[\'\"\.\s]?l"
	reg2 = r"commercial driver[\'s\s]?(\'s)? license"
	if 	re.findall(reg1,text,flags=re.IGNORECASE) or re.findall(reg2,text,flags=re.IGNORECASE):
		if "hazmat" or "class a" in text.lower():
			has_cdl = True
		elif "cdl permit" or "class b" in text.lower():
			has_cdl = False
		else:
			has_cdl = True
	else:
		has_cdl = False
	return has_cdl

login_sequence()
truckers_with_name_phone_email = []

cdl_count = 0
for index, i in enumerate(truckers):
	print "iteration " + str(index)
	resp = driver.request('GET', i[-1]) 
	if cdl_filter(resp.text):
		cdl_count += 1
		contact_info = get_name_number_and_email(resp)
		i = contact_info + i
		truckers_with_name_phone_email.append(i)
		print "cdl_count = "+str(cdl_count)
	if index%500 == 0:
		np.save("truckers_with_name_phone_email_cdl_filter_applied",truckers_with_name_phone_email)


np.save("truckers_with_name_phone_email_cdl_filter_applied",truckers_with_name_phone_email)
