import requests
from bs4 import BeautifulSoup
import tkinter as tk
import json
import threading
import time


searchRegion = "eu"







class App:

    def __init__(self):
        self.config = self.getConfig()
        self.run = False
        self.initWindow()
        self.initLayout()
        self.initNavbar()
        self.constructOutputTable()
        self.constructOptions()
        self.root.mainloop()
    def getConfig(self):
        with open(".\config.json", "r") as f:
            return json.load(f)
    def saveConfig(self):
        with open(".\config.json", "w") as f:
            configJson = json.dumps(self.config, indent = 4, sort_keys = True )
            f.write(configJson)
    def saveRefreshRate(self):
        try:
            self.config["options"]["refreshRate"] = int(self.refRateInput.get())
            self.refreshCounter["text"] = "Refresh: " + str(self.refRateInput.get())
        except:
            raise TypeError("Refresh rate must be an integer.")
    def initWindow(self):
        self.root = tk.Tk()
        self.root.title("ESO Market Tracker")
    def initLayout(self):
        self.navBarFrame = tk.Frame(master = self.root, width = 80, height = 400, bg = "grey" )
        self.navBarFrame.pack(fill = tk.Y, side = tk.LEFT)

        self.outputFrame = tk.Frame(master = self.root, width = 400, height = 400, bg = "lightgrey" )
        self.outputFrame.pack(fill = tk.BOTH, side = tk.LEFT, expand = True)
    def findBestDeal(self, itemId):
        #find Tamriel Trade Center URL of the item
        itemUrl = "https://{0}.tamrieltradecentre.com/pc/Trade/SearchResult?ItemID={1}&SortBy=LastSeen&Order=desc".format(searchRegion, itemId)
        logContents = ""
        #try to request the page
        try:
            htmlContent = requests.get(itemUrl)
            print(htmlContent.status_code)
            if htmlContent.status_code == 202:
                raise Exception("Connection to site succesfull but it seems like site is requesting captcha information. Visit {} and enter captcha.".format(itemUrl))
                return
        except Exception as e:
            print("Page loading failed. Exception: " + e)
            input()

        #parse the response into beautiful soup
        soup = BeautifulSoup(htmlContent.text, "html.parser")
        try:
            table = soup.find("table", { "class": "trade-list-table" })
            items = table.find_all("tr", { "class": "cursor-pointer" })
        except:
            with open("errorlog.html" , "w", encoding = "utf-8") as f:
                f.write("Tried Url: "+ itemUrl + "\n" + "ItemID: " + itemId + "\n" + htmlContent.text)

            raise Exception("Couldn't scrape the search result. Item ID might be wrong or page is down. Check errorlog.html to see the html tried.")
            return

        #get listings into data list
        data = []
        
        for item in items:
            try:
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
            except Exception as e:
                with open("errorlog.html", "r") as f:
                    logContents = f.read()
                with open("errorlog.html" , "w") as f:
                    f.write(logContents + "\n" + str(item) + "\n" + e)
                raise Exception("Failed to scrape search result. Item added to errorlog.html")
                continue


        #find the best deal
        bestDeal = data[0]
        for item in data:
            if item["price"] < bestDeal["price"]:
                bestDeal = item

        return bestDeal
    def constructOutputTable(self):
        self.tableFrame = tk.Frame(master = self.outputFrame, width = 350, height = 350,  bg = "white")
        self.tableFrame.pack(fill = tk.Y, side = tk.LEFT, padx = 20, pady = 20)
    def initNavbar(self):

        self.trackerButton = tk.Button( master = self.navBarFrame, command = lambda: self.EventHandler.handleTrackerButton(self), text = "Tracker", state = "active", width = 7, height = 2)
        self.trackerButton.pack( side = tk.TOP, padx = 2, pady = 20 )

        self.optionsButton = tk.Button( master = self.navBarFrame, command =lambda: self.EventHandler.handleOptionsButton(self), text = "Options", state = "normal", width = 7, height = 2 )
        self.optionsButton.pack( side = tk.TOP, padx = 2 )

        self.stopButton = tk.Button( master = self.navBarFrame, command = lambda: self.EventHandler.handleStopButton(self), text = "Stop", state = "disabled", width = 7, height = 2 )
        self.stopButton.pack( side = tk.BOTTOM )

        self.startButton = tk.Button( master = self.navBarFrame, command = lambda: self.EventHandler.handleStartButton(self), text = "Start", width = 7, height = 2 )
        self.startButton.pack( side = tk.BOTTOM )

        self.refreshCounter = tk.Label( master = self.navBarFrame, text = "Refresh: " + str(self.config["options"]["refreshRate"]))
        self.refreshCounter.pack( side = tk.BOTTOM )
    def constructOptions(self):
        self.optionsFrame = tk.Frame(master = self.outputFrame, width = 350, height = 350, bg = "white")
        
        
        #save button
        self.saveButton = tk.Button( master = self.optionsFrame, text = "Save", font = "Helvetica 16", command = lambda: self.EventHandler.handleSaveButton(self) )
        self.saveButton.pack( fill = tk.X , side = tk.TOP, ipady = 2)

        #refresh rate input
        self.refRateSettingsFrame = tk.Frame( master = self.optionsFrame , width = 150)
        
        self.refRateText = tk.Label(master = self.refRateSettingsFrame, pady = 10, text = "Refresh Rate (seconds): ")
        self.refRateInput = tk.Entry(master = self.refRateSettingsFrame, font = "Helvetica 14 bold",)
        self.refRateInput.insert(0, self.config["options"]["refreshRate"])
        self.refRateText.grid(column = 0, row = 1)
        self.refRateInput.grid(column = 1, row = 1)

        self.refRateSettingsFrame.pack(fill = tk.X, side = tk.TOP, pady = 4 )

        #edit items
        self.editItemsFrame = tk.Frame(master = self.optionsFrame, width = 150 )

        #self.itemBox = tk.Listbox( master = self.editItemsFrame, bg = "white" )
#
        #for index, item in enumerate(self.config["items"]):
        #    itemBox.insert( index , item["name"])
        
        self.itemBox = self.itemBox(self)
        
        self.editItemsAddButton = tk.Button( master = self.editItemsFrame, text = "Add", font = "Helvetica 14", command = lambda: self.EventHandler.handleEditItemsAdd(self) )
        self.editItemsEditButton = tk.Button( master = self.editItemsFrame, text = "Delete", font = "Helvetica 14", command = lambda: self.EventHandler.handleEditItemsDelete(self) )
        self.editItemsDeleteButton = tk.Button( master = self.editItemsFrame, text = "Edit", font = "Helvetica 14", command = lambda: self.EventHandler.handleEditItemsEdit(self) )

        self.editItemsAddButton.grid( column = 0, row = 0 )
        self.editItemsEditButton.grid( column = 0, row = 1 )
        self.editItemsDeleteButton.grid( column = 0, row = 2 )
        
        self.editItemsFrame.pack(fill = tk.X, side = tk.TOP, pady = 4 )

    class itemBox:
        def __init__(self, parentSelf):
            self.itemBox = tk.Listbox( master = parentSelf.editItemsFrame, bg = "white" )
            self.parent = parentSelf
            self.constructList()
            self.itemBox.grid(column = 1, row = 0, rowspan = 3)
        def constructList(self):
            items = self.parent.config["items"]
            for index, item in enumerate(items):
                self.itemBox.insert( index , item["name"])

        def refreshList(self):
            self.itemBox.delete(0, "end")
            self.constructList()
        def constructWindow(self, itemName="", itemId="", threshold=""):

            
            self.itemWindow = tk.Toplevel()
            
            itemNameText = tk.Label( master = self.itemWindow, text = "Item Name: ", font = "Helvetica 16 bold")
            itemIdText = tk.Label( master = self.itemWindow, text = "Item ID*: ", font = "Helvetica 16 bold")
            itemThresholdText = tk.Label( master = self.itemWindow, text = "Price Alert Threshold: ", font = "Helvetica 16 bold")

            itemNameInput = tk.Entry( master = self.itemWindow, font = "Helvetica 14")
            itemIdInput = tk.Entry( master = self.itemWindow, font = "Helvetica 14")
            itemThresholdInput = tk.Entry( master = self.itemWindow, font = "Helvetica 14")

            itemNameInput.delete(0, "end")
            itemIdInput.delete(0, "end")
            itemThresholdInput.delete(0, "end")

            itemNameInput.insert(0, itemName)
            itemIdInput.insert(0, itemId)
            itemThresholdInput.insert(0, threshold)

            itemNameText.grid(column = 0, row = 0)
            itemNameInput.grid(column = 1, row = 0)
            itemIdText.grid(column = 0, row = 1)
            itemIdInput.grid(column = 1, row = 1)
            itemThresholdText.grid(column = 0, row = 2)
            itemThresholdInput.grid(column = 1, row = 2)

            def saveWindow():
                try:
                    IdInput = int(itemIdInput.get())
                except:
                    raise Exception("ID can't be empty or must be integer")
                    return
                try:
                    nameInput = str(itemNameInput.get())
                except:
                    raise Exception("Invalid Name")
                    return
                    
                try:
                    thresholdInput = int(itemThresholdInput.get())
                except:
                    print("Alert threshold must be integer. Setting the value to 0")
                    thresholdInput = 0

                configFile = self.parent.config
                duplicateFound = False
                #check and edit duplicate
                for index, item in enumerate(configFile["items"]):
                    if duplicateFound is True:
                        continue
                    itemId = item["id"]
                    itemName = item["name"]
                    if itemId == IdInput or itemName == nameInput:
                        #duplicate found
                        duplicateFound = True
                        configFile["items"][index]["id"] = IdInput
                        configFile["items"][index]["name"] = nameInput
                        configFile["items"][index]["price_threshold"] = thresholdInput


                if duplicateFound is False:
                    newItem = {
                        "id": IdInput,
                        "name": nameInput,
                        "price_threshold": thresholdInput
                    }
                    configFile["items"].append(newItem)

                with open(".\config.json", "w") as f:
                    configJson = json.dumps(configFile, indent = 4, sort_keys = True )
                    f.write(configJson)
                
                self.refreshList()

            itemWindowSaveButton = tk.Button( master = self.itemWindow, text = "Save", font = "Helvetica 16 bold", command = saveWindow )
            itemWindowSaveButton.grid (column = 0, row = 3, columnspan = 2)
            


        def addItem(self):
            self.constructWindow()
        def editItem(self):
            selectedItem = self.itemBox.curselection()
            selectedItemIndex = selectedItem[0]
            #get item from config
            configItem = self.parent.config["items"][selectedItemIndex]
            
            self.constructWindow(configItem["name"], configItem["id"], configItem["price_threshold"])
            
        def deleteItem(self):
            selectedItem = self.itemBox.curselection()
            selectedItemIndex = selectedItem[0]
            self.parent.config["items"].pop(selectedItemIndex)
            self.parent.saveConfig()
            self.refreshList()

    def mainLoop(self):
        if self.run == True:
            while True:

                self.constructOutput()
                timeRemaining = self.config["options"]["refreshRate"]
                for i in range(timeRemaining):
                    timeRemaining -= 1
                    self.refreshCounter["text"] = "Refresh: " + str(timeRemaining)
                    time.sleep(1)
                    if self.run == False:
                        return

    class EventHandler:
        def handleStartButton(self):
            self.run = True
            self.startButton.config( state = "disabled" )
            self.stopButton.config( state = "normal" )
            self.loopThread = threading.Thread(target = self.mainLoop)
            self.loopThread.start()

        def handleStopButton(self):
            self.run = False
            self.refreshCounter["text"] = "Refresh: " + str(self.config["options"]["refreshRate"])
            self.stopButton.config( state = "disabled")
            self.startButton.config( state = "active")
            

        def handleTrackerButton(self):
            self.optionsFrame.pack_forget()
            self.tableFrame.pack(fill = tk.Y, side = tk.LEFT, padx = 20, pady = 20)

        def handleOptionsButton(self):
            self.tableFrame.pack_forget()
            self.optionsFrame.pack(fill = tk.Y, side = tk.LEFT, padx = 20, pady = 20)
        def handleSaveButton(self):
            self.saveRefreshRate()
        def handleEditItemsAdd(self):
            self.itemBox.addItem()
            
        def handleEditItemsEdit(self):
            self.itemBox.editItem()
        def handleEditItemsDelete(self):
            self.itemBox.deleteItem()
    def constructOutput(self):
        def constructColumn(item, row):
            for i in range(4):
                if i == 0:
                    boxContent = item["name"]
                if i == 1:
                    boxContent = "{0}g x {1} = {2}g".format(item["price"], item["amount"], item["totalPrice"])

                    if item["price"] <= config["items"][row]["price_threshold"]:
                        gridBox = tk.Frame(
                            master = self.tableFrame,
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
                    master = self.tableFrame,
                    borderwidth = 1
                )
                
                gridBox.grid(row = row, column = i)
                label = tk.Label(master = gridBox, text = boxContent, padx = 5, pady = 5)
                label.pack()

        def constructRow(config):
            itemConfig = config["items"]
            for i in range(len(itemConfig)):
                itemId = itemConfig[i]["id"]
                
                constructColumn(self.findBestDeal(itemId), i)

        with open(".\\config.json" , "r") as f:
            config = json.loads(f.read())
        constructRow(config)

app = App()