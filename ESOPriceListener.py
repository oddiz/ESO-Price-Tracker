import requests
from bs4 import BeautifulSoup
import tkinter as tk
import json
import threading
tamrielURL = "https://eu.tamrieltradecentre.com/pc/Trade/SearchResult?ItemID=5687&SortBy=LastSeen&Order=desc"

searchRegion = "eu"




def findBestDeal(itemId):
    #find Tamriel Trade Center URL of the item
    itemUrl = "https://{0}.tamrieltradecentre.com/pc/Trade/SearchResult?ItemID={1}&SortBy=LastSeen&Order=desc".format(searchRegion, itemId)
    
    #try to request the page
    try:
        htmlContent = requests.get(itemUrl)
        print(htmlContent.status_code)
        with open("./htmldump.html", "w", encoding="utf-8") as f: 
            f.write(htmlContent.text)
    except Exception as e:
        print("Page loading failed. Exception: " + e)
        input()

    #parse the response into beautiful soup
    soup = BeautifulSoup(htmlContent.text, "html.parser")
    table = soup.find("table", { "class": "trade-list-table" })
    items = table.find_all("tr", { "class": "cursor-pointer" })

    #get listings into data list
    data = []
    for item in items:
        itemName = item.find_all("div")[0].text.strip()
        itemPrice = item.find("td", { "class": "gold-amount" }).text.strip().splitlines()[0]
        itemPrice = float(itemPrice.replace(",", ""))
        itemAmount = int(item.find("td", { "class": "gold-amount" }).text.strip().splitlines()[6].strip())
        postTime = item.find("td", { "class": "bold hidden-xs" }).get("data-mins-elapsed") + " min ago"
        itemLocation = item.find_all("td", { "class": "hidden-xs" })[1].text.strip().splitlines()[0].replace(":", " ->")
        itemSeller = item.find("div", { "class": "text-small-width" }).text.strip()


        data.append({ 
            "name": itemName, 
            "price": itemPrice , 
            "amount": itemAmount, 
            "totalPrice": itemPrice*itemAmount, 
            "timeElapsed": postTime, 
            "location": itemLocation,
            "seller": itemSeller
        })

        with open("testing.html" , "w") as f:
            f.write(str(item))

    #find the best deal
    bestDeal = data[0]
    for item in data:
        if item["price"] < bestDeal["price"]:
            bestDeal = item

    return bestDeal



def constructOutput():
    

    def constructColumn(item, row):
        for i in range(4):
            if i == 0:
                boxContent = item["name"]
            if i == 1:
                boxContent = "{0}g x {1} = {2}g".format(item["price"], item["amount"], item["totalPrice"])

                if item["price"] <= config["items"][row]["price_threshold"]:
                    gridBox = tk.Frame(
                        master = tableFrame,
                        borderwidth = 1
                    )
                    gridBox.grid(row = row, column = i)
                    label = tk.Label(master = gridBox, text = boxContent, fg = "white", bg = "red", padx = 5, pady = 5)
                    label.pack()
                    continue
            if i == 2:
                boxContent = item["location"]
            if i == 3:
                boxContent = item["timeElapsed"]

            gridBox = tk.Frame(
                master = tableFrame,
                borderwidth = 1
            )
            gridBox.grid(row = row, column = i)
            label = tk.Label(master = gridBox, text = boxContent, padx = 5, pady = 5)
            label.pack()

    def constructRow(config):
        itemConfig = config["items"]
        for i in range(len(itemConfig)):
            itemId = itemConfig[i]["id"]
            
            constructColumn(findBestDeal(itemId), i)

    with open(".\\config.json" , "r") as f:
        config = json.loads(f.read())
    constructRow(config)


class EventHandler:

    def handleStartButton(self):
        startButton.config( state = "disabled" )
        stopButton.config( state = "normal" )
        constructOutput()

    def handleStopButton(self):
        stopButton.config( state = "disabled")
        startButton.config( state = "active")

    def handleTrackerButton(self):
        tableFrame.pack(fill = tk.Y, side = tk.LEFT, padx = 20, pady = 20)

    def handleOptionsButton(self):
        tableFrame.pack_forget()

eventHandler = EventHandler()
root = tk.Tk()
root.title("ESO Market Tracker")

navBarFrame = tk.Frame(master = root, width = 80, height = 400, bg = "grey" )
navBarFrame.pack(fill = tk.Y, side = tk.LEFT)

outputFrame = tk.Frame(master = root, width = 400, height = 400, bg = "lightgrey" )
outputFrame.pack(fill = tk.BOTH, side = tk.LEFT, expand = True)

#construct grids
tableFrame = tk.Frame(master = outputFrame, width = 350, height = 350,  bg = "white")
tableFrame.pack(fill = tk.Y, side = tk.LEFT, padx = 20, pady = 20)
    
stopButton = tk.Button( master = navBarFrame, command = eventHandler.handleStopButton, text = "Stop", state = "disabled", width = 7, height = 2 )
stopButton.pack( side = tk.BOTTOM )

startButton = tk.Button( master = navBarFrame, command = eventHandler.handleStartButton, text = "Start", width = 7, height = 2 )
startButton.pack( side = tk.BOTTOM )

trackerButton = tk.Button( master = navBarFrame, command = eventHandler.handleTrackerButton, text = "Tracker", state = "active", width = 7, height = 2)
trackerButton.pack( side = tk.TOP, padx = 2, pady = 20 )

optionsButton = tk.Button( master = navBarFrame, command = eventHandler.handleOptionsButton, text = "Options", state = "normal", width = 7, height = 2 )
optionsButton.pack( side = tk.TOP, padx = 2 )

root.mainloop()

