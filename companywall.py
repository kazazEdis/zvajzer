import requests
from bs4 import BeautifulSoup
import io
import pytesseract
from PIL import Image

# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"  # Windows tesseract location
# pytesseract.pytesseract.tesseract_cmd = ‘/app/.apt/usr/bin/tesseract’ 


def profile_link(query):
    html_doc = requests.get('http://www.simple-cw.hr/Home/Search?n=' + query).text  # Get Companywall profile address
    soup = BeautifulSoup(html_doc, 'html.parser')
    profile_link_selector = soup.select('tr td a')
    profile_link = ''
    for i in profile_link_selector:
        profile_link = i['href']
    return profile_link


def website(soup):
    try:
        res = soup.find('div', {'class': "col-sm-4"}, text="\r\n\t\t\t\t\t\t\t\t\t\tweb\r\n\t\t\t\t\t\t\t\t\t").find_next_sibling("div").text
        res = res.replace('\n', '')
        return res
    except AttributeError:
        pass

def size(soup):
    badChars = ['\r', '\n', '\t']
    try:
        res = soup.find('div', {'class': "col-sm-4"}, text="\r\n\t\t\t\t\t\t\t\t\tVeličina poduzeća\r\n\t\t\t\t\t\t\t\t").find_next_sibling("div").text
        for badChar in badChars:
            res = res.replace(badChar,'')
    except AttributeError:
            res = 'Nepoznato'
    return res

def nkd(soup):
    badChars = ['\r', '\n', '\t', ';', '-']
    res = soup.find('div', {'class': "col-sm-4"}, text="\r\n\t\t\t\t\t\t\t\tNKD:\r\n\t\t\t\t\t\t\t").find_next_sibling("div").text
    for badChar in badChars:
        res = res.replace(badChar,'')
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
        for i in contacts_soup:
            contact_img_links.append(i['src'])
    except AttributeError:
        pass
    #  Brojevi Faxa
    try:
        company_fax_soup = soup.find('div', itemprop="faxNumber")
        contacts_fax = company_fax_soup.findAll('img')
        for i in contacts_fax:
            contact_img_links.append(i['src'])
    except AttributeError:
        pass

    return contact_img_links


def ocr(img_addresses):
    res = []
    for img_address in img_addresses:
        try:
            response = requests.get('http://www.simple-cw.hr' + img_address)  # Dohvati sliku
            img = Image.open(io.BytesIO(response.content))  # Otvori sliku
            text = pytesseract.image_to_string(img).rstrip('\n\x0c')  # Konvertiraj sliku u text i obriši višak znakova
            text_witouth_space = text.replace(' ', '').replace('\n', ',').lstrip('0').split(",")  # Obriši razmake

            for number in text_witouth_space:
                n = str(number).lstrip('0')
                ln = len(n)
                if n not in res:
                    if ln <= 10 and ln > 6:
                        res.append(n)

        except:
            continue
    return res
