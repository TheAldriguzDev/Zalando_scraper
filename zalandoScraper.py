import requests
import bs4 as bs
import dhooks
from dhooks import *

class Zalando:

    def __init__(self, url, webhook):
        self.url = url
        self.stock = []
        self.size = []
        self.pid = []
        self.image = ""
        self.name = ""
        self.color = ""
        self.price = ""
        self.session = requests.Session()
        self.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-language": "it-IT,it;q=0.9,en-IT;q=0.8,en;q=0.7,si-LK;q=0.6,si;q=0.5,en-US;q=0.4",
            "sec-ch-ua": "\"Not_A Brand\";v=\"99\", \"Google Chrome\";v=\"109\", \"Chromium\";v=\"109\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"macOS\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
        }
        self.webhook = webhook

    def scraper(self):
        productPage = self.session.get(self.url, headers=self.headers, timeout=10).text
        soup = bs.BeautifulSoup(productPage, 'html.parser')
        productPage = productPage.split(',"currency":"')
        for i in range(len(productPage)):
            if '},"price":{"original":{"amount":' in productPage[i]:
                parsedText = productPage[i]

                size1 = parsedText[parsedText.index('"size":"')+8:]
                actualSize = size1[0: size1.index('"')]

                searchpid = actualSize +  '","sku":"'
                tempPid = parsedText[parsedText.index(searchpid)+len(searchpid):]
                actualPid = tempPid[0: tempPid.index('"')]
                
                tempStock = parsedText[parsedText.index('stock":{"quantity":"')+20:]
                actualStock = tempStock[0: tempStock.index('"')]
                
                if "-" in actualPid:
                    self.size.append(actualSize)
                    self.pid.append(actualPid)
                    self.stock.append(actualStock)
                else:
                    # bad pid found
                    pass
        self.name = soup.find("span", {"class": "EKabf7 R_QwOV"}).text
        self.image = soup.find("img", {"class": "_0Qm8W1 u-6V88 FxZV-M _2Pvyxl JT3_zV EKabf7 mo6ZnF _1RurXL mo6ZnF _7ZONEy"})["src"]
        self.price = soup.find("p", {"class": "_0Qm8W1 uqkIZw FxZV-M pVrzNP"}).text.strip()
        self.color = soup.find("p", {"class": "_0Qm8W1 u-6V88 dgII7d pVrzNP zN9KaA"}).text.strip()
        self.sendWebhook()

    def sendWebhook(self):
        hook = Webhook(self.webhook)
        embed = Embed(
            description="Loompaland scraper",
            color=15813039,
            timestamp="now"
        )

        sizeMessage = ""
        stockMessage = ""
        pidMessage = ""
        for i in range(len(self.size)):
            sizeMessage += self.size[i] + " \n"
            stockMessage += self.stock[i] + " \n"
            pidMessage += self.pid[i] + " \n"

        embed.set_title("Loompaland stock scraped")
        embed.add_field(name="Name", value=self.name + self.color)
        embed.add_field(name="Price", value=self.price)
        embed.add_field(name="Name", value=self.name)
        embed.add_field(name="Size", value=sizeMessage)
        #embed.add_field(name="Pid", value=pidMessage)
        embed.add_field(name="Stock", value=stockMessage)
        embed.set_thumbnail(url=self.image)
        hook.send(embed=embed)
        
if __name__ == "__main__":
    zalandoScraper = Zalando("ENTER_PRODUCT_URL", "DISCORD_WEBHOOK")
    zalandoScraper.scraper()
