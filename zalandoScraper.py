import requests
import bs4 as bs
import dhooks
from dhooks import *
import random

class Zalando:

    def __init__(self, url, webhook, proxyList, proxyStatus):
        self.url = url
        self.stock = []
        self.size = []
        self.pid = []
        self.image = ""
        self.name = ""
        self.color = ""
        self.price = ""
        self.sku = f'{url.split(".html")[0].split("-")[-2]}-{url.split(".html")[0].split("-")[-1]}'
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
        self.proxyList = proxyList
        self.proxyStatus = proxyStatus
        
    def scraper(self):
        if self.proxyStatus == "YES":
            print("Getting the site using proxies")
            proxy = random.choice(self.proxyList)
            proxyip = proxy.split(":")[0]
            proxyPort = proxy.split(":")[1]
            proxyuser = proxy.split(":")[2]
            proxypsw = proxy.split(":")[3]
            try: 
                proxies = {
                    'http': 'http://'+proxyuser+':'+proxypsw+'@'+proxyip+':'+proxyPort+'',
                    'https': 'https://'+proxyuser+':'+proxypsw+'@'+proxyip+':'+proxyPort+'',
                }
                productPage = self.session.get(self.url, headers=self.headers, timeout=10, proxies=proxies).text
                # you can also add bad response status error handling
                self.parser(productPage)
            except Exception as e:
                try:
                    print("Retrying")
                    proxies = {
                        'http': 'http://'+proxyuser+':'+proxypsw+'@'+proxyip+':'+proxyPort+'',
                    }
                    productPage = self.session.get(self.url, headers=self.headers, timeout=10, proxies=proxies).text
                    # you can also add bad response status error handling
                    self.parser(productPage)
                except:
                    print("Proxy not supported")
        else:
            print("Getting the product without proxy")
            productPage = self.session.get(self.url, headers=self.headers, timeout=10).text
            # you can also add bad response status error handling
            self.parser(productPage)

    def parser(self, productPage):
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

        clickUrl = [f"https://www.zalando.it/catalogo/?q={self.sku}",
                f"https://www.zalando.de/katalog/?q={self.sku}",
                f"https://www.zalando.de/katalog/?q={self.sku}",
                f"https://www.zalando.nl/catalogus/?q={self.sku}",
                f"https://www.zalando.at/katalog/?q={self.sku}",
                f"https://www.zalando.pl/katalog/?q={self.sku}",
        ]

        sizeMessage = ""
        pidMessage = ""
        for i in range(len(self.size)):
            if self.stock[i] == "OUT_OF_STOCK":
                sizeMessage += f':red_circle: {self.size[i]} [{self.stock[i]}] \n'
            elif self.stock[i] == "ONE":
                sizeMessage += f':orange_circle: {self.size[i]} [{self.stock[i]}]\n'
            elif self.stock[i] == "TWO":
                sizeMessage += f':yellow_circle: {self.size[i]} [{self.stock[i]}]\n'
            else:
                sizeMessage += f':green_circle: {self.size[i]} [{self.stock[i]}]\n'
            pidMessage += self.pid[i] + " \n"

        embed.set_title("Loompaland stock scraped")
        embed.add_field(name="Name", value=self.name + self.color)
        embed.add_field(name="Price", value=self.price)
        embed.add_field(name="Name", value=self.name)
        embed.add_field(name="Size", value=sizeMessage)
        embed.add_field(name="Pid", value=f'```{pidMessage}```')
        embed.add_field(name="Load page", value=f'[IT]({clickUrl[0]}) [DE]({clickUrl[1]}) [FR]({clickUrl[2]}) [NL]({clickUrl[3]}) [UK]({clickUrl[4]}) [PL]({clickUrl[5]})', inline=False)
        embed.set_thumbnail(url=self.image)
        hook.send(embed=embed)
        
if __name__ == "__main__":
    proxylist = ["ip:port:user:psw",
            "ip:port:user:psw"] # this is the format supported
    proxyStatus = "YES" # change to NO if you don't want to use proxies
    zalandoScraper = Zalando("ENTER PRODUCT URL", "DISCORD_WEBHOOK", proxylist, proxyStatus)
    zalandoScraper.scraper()
