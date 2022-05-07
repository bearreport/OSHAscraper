import pandas as pd
import requests
from bs4 import BeautifulSoup

URL = "https://www.osha.gov/fatalities"
#I don't know why this has to be prefaced with r but it works
path=r"C:\Users\joshua.bayer\Documents\src\geckodriver.exe"


#grab the main OSHA page
page = requests.get(URL)

#pass page content to beautiful soup
soup = BeautifulSoup(page.text, 'html.parser')

#find the table
table = soup.find(id="incSum")

#convert to dataframe
df = pd.read_html(str(table))[0]

#lose all the non-fine issued
#df_filtered = df[df['Citation Issued Related to Fatality']  == "Yes"][:1]

#get list of secondary links to hit
details = df['Inspection Number'].values.tolist()

#generate detail links
links = []
detail_url_base = "https://www.osha.gov/pls/imis/establishment.inspection_detail?id="
detail_url_tag = ".015"
for deets in details:
	links.append(detail_url_base + str(int(deets)) + detail_url_tag)

#build link/inspection number dictionary
link_dict = {}
for i in range(len(links)):
	link_dict[links[i]] = int(details[i])

#make a list
inspections = []

#iterate through detail links
count = 0
for link in links:
	#this is just for logging so you don't get bored while the script runs
		print(count)
		print(link)
		print(link_dict[link])
		page = requests.get(link)
		soup = BeautifulSoup(page.text, 'html.parser')
		try:
			inspection = soup.find(id="maincontain").get_text()
			inspections.append(inspection)
		except:
			inspections.append("No inspection provided")
		count += 1

df['Inspection'] = inspections

df.fillna(0, inplace=True)

#I stole this from stackoverflow I don't know what it does but it keeps it from breaking
df = df.applymap(lambda x: x.encode('unicode_escape').
                 decode('utf-8') if isinstance(x, str) else x)

df.to_excel("OSHA_Fatalities_with_inspections.xlsx")