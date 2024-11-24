import time
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

service = Service(executable_path="chromedriver.exe")
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
driver = webdriver.Chrome(service=service, options=options)

'''
DINGE DIE HINZUGEFÜGT WERDEN **MÜSSEN**:
- Eigene Filter (nach Keywords in der Description, Titel)
- Emails wenn passende Inserate hochgeladen werden
- Vlt. n schöneres Interface idk
- Docker Compatibility 
- 24/7 Einsatz mit Push-Benarichtigung / Email
- "verbose-mode", der die Titel der Listings & ihre Preise anzeigt
'''

class Listing:
    def __init__(self, title, price, shipping, description, date_published, place, url):
        self.title = title
        self.price = price
        self.shipping = shipping
        self.description = description
        self.url = url
        self.date_published = date_published
        self.place = place

processedListings = []

def scrapeDescription(url):
    driver.get(url)

    soup = BeautifulSoup(driver.page_source, "lxml")
    try:
        description = soup.find("p", {"class": "text-force-linebreak"}).decode_contents().replace("<br/>", "\n").strip()
    except:
        description = "NONE"
    return description

def scrapeKleinanzeigen(url):
    driver.get(url)

    soup = BeautifulSoup(driver.page_source, "lxml")
    listings = soup.find_all("li", {"class": "ad-listitem"})

    for item in listings:
        # Url & Title
        urlContents = item.find_all("a", {"class": "ellipsis"})
        for content in urlContents:
            title = content.decode_contents()
            listing_url = "https://www.kleinanzeigen.de" + content["href"]
        # Price
        if item.find("p", {"class": "aditem-main--middle--price-shipping--price"}) is not None:
            price = item.find("p", {"class": "aditem-main--middle--price-shipping--price"}).decode_contents()
            if "€" in price:
                price = price.replace("€", "")
            if "VB" in price:
                price = price.replace("VB", "")
            if "Zu verschenken" in price:
                price = "0"
            price = price.strip()
        # Shipping
        if item.find("span", {"class": "simpletag tag-with-icon"}) is not None:
            shipping = item.find("span", {"class": "simpletag tag-with-icon"}).decode_contents().split(">")[2].strip()
        else:
            shipping = "NONE"
        # Description
        '''
        if item.find("p", {"class": "aditem-main--middle--description"}) is not None:
            description = item.find("p", {"class": "aditem-main--middle--description"}).decode_contents().strip()
        '''    
        description = scrapeDescription(listing_url)
        # Place 
        if item.find("div", {"class": "aditem-main--top--left"}) is not None:
            place = item.find("div", {"class": "aditem-main--top--left"}).decode_contents().split(">")[2].strip()
        # Date 
        if item.find("div", {"class": "aditem-main--top--right"}) is not None:
            try:
                date_published = item.find("div", {"class": "aditem-main--top--right"}).decode_contents().split(">")[2].strip()
            except:
                continue
        
        processedListings.append(Listing(title, price, shipping, description, date_published, place, listing_url))

query = "macbook"
pages = 15
max_price = 150

for i in range(pages):
    print("[info:] '" + query + "' Scraping Page: (" + str(i) + "/" + str(pages) + ") ...")
    scrapeKleinanzeigen("https://www.kleinanzeigen.de/s-seite:" + str(i) + "/" + query + "/k0")

with open("all_listings.json", "w") as f:
    json.dump("", f, indent = 6)
with open("final_listings.json", "w") as f:
    json.dump("", f, indent = 6)

for listing in processedListings:

    print("[info:] '" + query + "' Filtering at Price: " + str(max_price) + " ...")

    jsonString = json.dumps(listing.__dict__)
    with open("all_listings.json", "a") as f:
        json.dump(listing.__dict__, f, indent = 6)

    try:
        if int(listing.price) > max_price:
            continue
    except:
        continue

    print("[HIT:] '" + query + "' -> '" + listing.title + "' at " + listing.price + "€")

    print(listing.description)
    print(listing.date_published)
    print(listing.place)
    print(listing.shipping)
    print(listing.url)
    print("\n") 

    jsonString = json.dumps(listing.__dict__)
    with open("final_listings.json", "a") as f:
        json.dump(listing.__dict__, f, indent = 6)
    
print("\n[info:] '" + query + "' FINISHED: look into -> 'final-listings.json' ...")