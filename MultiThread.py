from bs4 import BeautifulSoup
import requests.exceptions
from urllib.parse import urlsplit
from collections import deque
import re
from PyQt5 import QtCore


class GetThread(QtCore.QThread):
    addNewLine = QtCore.pyqtSignal(str)  # Luodaan uusi singaali joka ottaa yhden str argumentin
    finished = QtCore.pyqtSignal()     # Luodaan signaali jota käytetään kertomaan, että thread on valmis
    progres = QtCore.pyqtSignal(int)   # Signaali prosentti osuuden lähettämiseen

    def __init__(self, string, number):
        QtCore.QThread.__init__(self)
        self.startUrl = string  #Alustetaan tiedot jotka saadaan gui objektilta, kun threadiä kutsutaan
        self.times = number
        self.filePath = "Libs\mails.txt"    # Filepath

    def __del__(self):
        self.wait()

    def main(self):
        start = self.startUrl  # Otetaan aloitus url guin lähettämästä stringistä
        if start == "":
            start = "https://en.wikipedia.org/wiki/Email"
        new_urls = deque([start])  # Luodaan deque
        processed_urls = set()
        emails = set()
        sites = 1
        amount = self.times  # Otetaan site määrä Guin lähettämstä spinboxin numerosta
        while len(new_urls) and sites <= amount:
            url = new_urls.popleft()  # Otetaan url, laitetaan se käsiteltyihin ja aloitetaan uusien etsintä
            processed_urls.add(url)
            parts = urlsplit(url)
            base_url = "{0.scheme}://{0.netloc}".format(parts)
            path = url[:url.rfind('/') + 1] if '/' in parts.path else url
            line = "Site number " + str(sites) + ": %s" % url
            prosent = round(sites/amount*100, 2)
            self.addNewLine.emit(line)   # Lähetetään signaali ja str sen mukana
            self.progres.emit(prosent)  # Lähetetään prosentti luku
            try:  # Testataan käytössä olevan urlin paikkansa pitävyys
                response = requests.get(url)  # Kutsutaan sivua
            except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
                continue    #Jos url ei ole kunnolinen/ei saada yhteyttä hypätään sen yli
            new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.text,
                                        re.I))  # etsitään takaisin saadusta txt tiedostosta email osoitteita
            with open(self.filePath, 'r') as cs:  # Tarkistetaan ettei oteta kuvia tai tupla osoitteita
                data = cs.read()
            with open(self.filePath, 'a') as file:
                for mail in new_emails:
                    if mail not in data and mail[-4:] != '.png':
                        file.write(mail + '\n')
            soup = BeautifulSoup(response.text, "html.parser")  # Parsitaan .txt takaisin html tiedostoksi
            for anchor in soup.find_all("a"):  # Etsitään linkki tageja joissa on linkki
                link = anchor.attrs["href"] if "href" in anchor.attrs else ''
                if link.startswith('/'):
                    link = base_url + link
                if link.startswith(
                        'http') and not link in new_urls and not link in processed_urls:  # Tarkistetaan ettei sama url tule kahdesti
                    new_urls.append(link)
            sites += 1  # Lisätään laskuriin yksi luku
        self.finished.emit()    # Lähetetään lopetus signaali

    def run(self):  # run funktio on PyQt oma joka suoritetaan kun threadia kutsutaan
        '''
        Tekijän huom. Vaikka run on ensimmäinen funktio minkä PyQt Thread suorittaa,
        ei sille voi suoraan antaa argumentteja kutsussa. Se kuitenkin rakennetaan
        Threadin alussa, mikä mahdollistaa myös argumenttejen lähettämisen classiin, mutta ei suoraan funktioon.
        '''
        self.main()     # Mennään suoraan main osaan