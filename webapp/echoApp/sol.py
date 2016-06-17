import re
import mechanize
from bs4 import BeautifulSoup

def get_links (inp):

	br = mechanize.Browser()

	br.open ("https://ttlc.intuit.com")

	br.select_form (nr=1)

	br.form["q"] = inp

	response = br.submit ()

	soup = BeautifulSoup(response.get_data(), 'html.parser')

	l = soup.findAll ("a",{"class":"post-subject"})

	linkList = []
	for ele in l :
		linkList.append("https://ttlc.intuit.com"+ele['href'])
	return linkList
