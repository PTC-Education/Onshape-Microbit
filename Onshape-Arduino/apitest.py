import json 
import requests # type: ignore
import serial # type: ignore
from math import radians
from time import sleep

# === functions ===
def getIds(url, wv):
  urlArr = url.split("/")
  dIndex = urlArr.index("documents")
  DID = urlArr[dIndex+1]
  eIndex = urlArr.index("e")
  EID = urlArr[eIndex+1]
  wvIndex = urlArr.index(wv)  
  WVID = urlArr[wvIndex+1] 
  return DID, EID, WVID

def potToRads(pot, min, max):
    range = abs(min - max)
    degs = min + pot/1024*range
    return radians(degs)

def changeColor(on):
    for prop in partProperties:
        if prop['name'] == 'Appearance':
            if on:
                prop['value']['opacity'] = 255
            else:
                prop['value']['opacity'] = 127
    metadataResponse['properties'] = partProperties
    payload = metadataResponse
    response = requests.post(
        "https://cad.onshape.com/api/metadata/d/{}/w/{}/e/{}/p/{}".format(
            partDID, partWID, partEID, ledID
        ),  
        auth=(API_ACCESS, API_SECRET), 
        headers={
            "Accept": "application/json;charset=UTF-8; qs=0.09", 
            "Content-Type": "application/json"
        },
        json=payload
    ) 
    
# get API keys
with open("APIKey.json") as f:
    data = json.load(f)
    API_ACCESS = data['access']
    API_SECRET = data['secret']

# get robot DID, EID, WID
assemURL = "https://cad.onshape.com/documents/62ebdfd4b2a7228795d6a890/w/fc9f37f67adb8886b6d652d4/e/6b4d163d1d4243d4bb17455f"
DID, EID, WID = getIds(assemURL, "w")
partURL = "https://cad.onshape.com/documents/62ebdfd4b2a7228795d6a890/w/fc9f37f67adb8886b6d652d4/e/e92507311dbebaf3520d6cef"
partDID, partEID, partWID = getIds(partURL, "w")

# get the LED part ID
response = requests.get(
    "https://cad.onshape.com/api/parts/d/{}/w/{}/e/{}/".format(
        partDID, partWID, partEID
    ), 
    auth=(API_ACCESS, API_SECRET), 
    headers={
        "Accept": "application/json;charset=UTF-8; qs=0.09", 
        "Content-Type": "application/json"
    }
) 
response = response.json() 
ledID = None
for part in response:
    if part['name'] == 'LED':
        ledID = part['partId']
# get the LED metadata
response = requests.get(
    "https://cad.onshape.com/api/metadata/d/{}/w/{}/e/{}/p/{}".format(
        partDID, partWID, partEID, ledID
    ), 
    auth=(API_ACCESS, API_SECRET), 
    headers={
        "Accept": "application/json;charset=UTF-8; qs=0.09", 
        "Content-Type": "application/json"
    }
) 
metadataResponse = response.json() 
partProperties = metadataResponse['properties']

# get the mates from the matevalues API endpoint
response = requests.get(
    "https://cad.onshape.com/api/assemblies/d/{}/w/{}/e/{}/matevalues".format(
        DID, WID, EID
    ), 
    auth=(API_ACCESS, API_SECRET), 
    headers={
        "Accept": "application/json;charset=UTF-8; qs=0.09", 
        "Content-Type": "application/json"
    }
) 
response = response.json()
# go through the json matevalues to find the desired mates
for mate in response["mateValues"]:
    if mate['mateName'] == "Pot1":
        pot1 = mate
    elif mate['mateName'] == "Pot2":
        pot2 = mate
    elif mate['mateName'] == "Pot3":
        pot3 = mate

# connect to serial port (the arduino IDE gave me the address)
ser = serial.Serial("/dev/cu.usbmodem11301", 115200, timeout=0.1)

oldPot1 = 0
oldPot2 = 0
oldPot3 = 0
led = False

while True:
    latest = None
    while ser.in_waiting:
        latest = ser.readline().decode().strip()
    if latest:
        arr = latest.split("|")
        pot1Pos = potToRads(int(arr[0]), 0, 360)
        pot2Pos = potToRads(int(arr[1]), 0, 360)
        pot3Pos = potToRads(int(arr[2]), 0, 360)
        
        # if there is a reasonable change, send new values via API
        if abs(oldPot1 - pot1Pos) > 0.1 or abs(oldPot2 - pot2Pos) > 0.1 or abs(oldPot3 - pot3Pos) > 0.1:
            pot1["rotationZ"] = pot1Pos
            pot2["rotationZ"] = pot2Pos
            pot3["rotationZ"] = pot3Pos
            print(str(pot1Pos) + " | " + str(pot2Pos) + " | " + str(pot3Pos))
            # post the updated json back to the matevalues API endpoint
            response = requests.post(
                "https://cad.onshape.com/api/assemblies/d/{}/w/{}/e/{}/matevalues".format(
                    DID, WID, EID
                ), 
                auth=(API_ACCESS, API_SECRET), 
                headers={
                    "Accept": "application/json;charset=UTF-8; qs=0.09", 
                    "Content-Type": "application/json"
                },
                json = {"mateValues":[pot1, pot2, pot3]}
            )
    
        oldPot1 = pot1Pos
        oldPot2 = pot2Pos
        oldPot3 = pot3Pos

    response = requests.get(
        "https://cad.onshape.com/api/assemblies/d/{}/w/{}/e/{}/matevalues".format(
            DID, WID, EID
        ), 
        auth=(API_ACCESS, API_SECRET), 
        headers={
            "Accept": "application/json;charset=UTF-8; qs=0.09", 
            "Content-Type": "application/json"
        }
    ) 
    response = response.json()
    for mate in response["mateValues"]:
        if mate['mateName'] == "SPDT":
            SPDT = mate['rotationZ']
            if SPDT < 2.9 and not led:
                ser.write(("LEDON" + "\n").encode())
                led = True
                changeColor(True)
            elif SPDT > 3.2 and led:
                ser.write(("LEDOFF" + "\n").encode())          
                led = False
                changeColor(False)

    sleep(0.1)