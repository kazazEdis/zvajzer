import requests
from bs4 import BeautifulSoup
import io
import pytesseract
from PIL import Image

# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"  # Windows tesseract location
pytesseract.pytesseract.tesseract_cmd = ‘/app/.apt/usr/bin/tesseract’ 

# Get Companywall profile address
def profile_link(query):
    html_doc = requests.get('http://www.simple-cw.hr/Home/Search?n=' + query).text
    soup = BeautifulSoup(html_doc, 'html.parser')
    profile_link_selector = soup.select('tr td a')
    profile_link = ''
    for i in profile_link_selector:
        profile_link = i['href']
    return profile_link


def nkd(soup):
    select = soup.find('div', {'class': "col-sm-4"}, text="\r\n\t\t\t\t\t\t\t\tNKD:\r\n\t\t\t\t\t\t\t").find_next_sibling("div")
    res = str(select).lstrip('<div class="col-sm-8">').replace('\r', '').replace('\n', '').replace('\t', '').rstrip(';</div>')
    return res


def odgovorne_osobe(soup):
    #  Odgovorne osobe
    company_odgovorne_osobe_soup = soup.findAll('div', {'class': "tbl-row"})
    odgovorne_osobe = []
    for i in company_odgovorne_osobe_soup:
        a = i.text.replace('  ', '')
        b = a.replace('\n', '')
        odgovorne_osobe.append(b)
    return odgovorne_osobe


def contact_imgs(soup):
    #  Brojevi telefona
    contact_img_links = []  # Linkovi koji vode do brojeva telefona u img formatu.
    company_contacts_soup = soup.find('div', itemprop="telephone")
    try:
        contacts_soup = company_contacts_soup.findAll('img')
    except AttributeError:
        print('Company not found!')
        exit()

    for i in contacts_soup:
        contact_img_links.append(i['src'])
    try:
        company_fax_soup = soup.find('div', itemprop="faxNumber")
        contacts_fax = company_fax_soup.findAll('img')
        for i in contacts_fax:
            contact_img_links.append(i['src'])
    except AttributeError:
        pass

    return contact_img_links


def ocr(img_addresses):
    brojevi_telefona = []
    for img_address in img_addresses:
        response = requests.get('http://www.simple-cw.hr' + img_address)  # Dohvati sliku
        img = Image.open(io.BytesIO(response.content))  # Otvori sliku
        text = pytesseract.image_to_string(img).rstrip('\n\x0c')  # Konvertiraj sliku u text i obriši višak znakova
        text_witouth_space = text.replace(' ', '').lstrip('0')  # Obriši razmake
        if text_witouth_space not in brojevi_telefona:  # Provjeri duplikate u popisu brojeva
            brojevi_telefona.append(text_witouth_space)  # Dodaj broj na popis brojeva
    return brojevi_telefona
