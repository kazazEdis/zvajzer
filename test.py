import requests
from bs4 import BeautifulSoup

html_doc = requests.get('http://www.simple-cw.hr/tvrtka/s-c-projecting-d-o-o/67870').text  # HTML Request
soup = BeautifulSoup(html_doc, 'lxml')  # HTML file

select = str(soup.find('div', {'class': "col-sm-4"}, text="\r\n\t\t\t\t\t\t\t\tNKD:\r\n\t\t\t\t\t\t\t").find_next_sibling("div"))
strip = str(select[0]).lstrip('<div class="col-sm-8">\n\t')
nkd = strip.rstrip('\n\t</div>')
print(repr(select))
