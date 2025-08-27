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

# get API keys
with open("APIKey.json") as f:
    data = json.load(f)
    API_ACCESS = data['access']
    API_SECRET = data['secret']

# get robot DID, EID, WID
URL = "https://cad.onshape.com/documents/f26e641e6881a11760822b61/w/f3653011fe26c2738eef1e84/e/4d3237caadef4f1d42dec690"
DID, EID, WID = getIds(URL, "w")

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
    if mate['mateName'] == "Base_Mate":
        baseMate = mate
    elif mate['mateName'] == "Shoulder_Mate":
        shoulderMate = mate
    elif mate['mateName'] == "Arm_Mate":
        armMate = mate

# connect to serial port (the arduino IDE gave me the address)
ser = serial.Serial("/dev/cu.usbmodem11301", 115200, timeout=0.1)

oldBase = 0
oldShoulder = 0
oldArm = 0

while True:
    latest = None
    while ser.in_waiting:
        latest = ser.readline().decode().strip()
    if latest:
        arr = latest.split("|")
        basePos = potToRads(int(arr[0]), 0, 360)
        shoulderPos = potToRads(int(arr[1]), -90, 90)
        armPos = potToRads(int(arr[2]), -90, 90)
        
        # if there is a reasonable change, send new values via API
        if abs(oldBase - basePos) > 0.1 or abs(oldShoulder - shoulderPos) > 0.1 or abs(oldArm - armPos) > 0.1:
            baseMate["rotationZ"] = basePos
            shoulderMate["rotationZ"] = shoulderPos
            armMate["rotationZ"] = armPos
            print(str(basePos) + " | " + str(shoulderPos) + " | " + str(armPos))
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
                json = {"mateValues":[baseMate, shoulderMate, armMate]}
            ) 
    
        oldBase = basePos
        oldShoulder = shoulderPos
        oldArm = armPos