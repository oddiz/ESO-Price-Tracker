import requests
from bs4 import BeautifulSoup


tamrielURL = "https://eu.tamrieltradecentre.com/pc/Trade/SearchResult?ItemID=5687&SortBy=LastSeen&Order=desc"





def getItems(pageURL):
    
    try:
        htmlContent = requests.get(pageURL)
        print(htmlContent.status_code)
        with open("./htmldump.html", "w", encoding="utf-8") as f: 
            f.write(htmlContent.text)
    except Exception as e:
        print("Page loading failed. Exception: " + e)
        input()




    soup = BeautifulSoup(htmlContent.text, "html.parser")
    table = soup.find("table", { "class": "trade-list-table" })
    items = table.find_all("tr", { "class": "cursor-pointer" })

    data = []

    for item in items:
        itemName = item.find("div", { "class": "item-quality-legendary" }).text.strip()
        itemPrice = item.find("td", { "class": "gold-amount" }).text.strip().splitlines()[0]
        itemPrice = float(itemPrice.replace(",", ""))
        itemAmount = int(item.find("td", { "class": "gold-amount" }).text.strip().splitlines()[6].strip())
        postTime = item.find("td", { "class": "bold hidden-xs" }).get("data-mins-elapsed") + " min ago"
        itemLocation = item.find_all("td", { "class": "hidden-xs" })[1].text.strip().splitlines()[0].replace(":", " ->")
        data.append({ "Item": itemName, "Price": itemPrice , "Amount": itemAmount, "Total Price": itemPrice*itemAmount, "Time Elapsed": postTime, "Location": itemLocation })

    with open("testing.html" , "w") as f:
        f.write(str(item))

    return data

print(getItems(tamrielURL))