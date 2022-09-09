import requests
import json
import os
import time
from flask import Flask, render_template, request, url_for
import concurrent.futures as cf

app=Flask(__name__)

OctoPrint_instance = "127.0.0.1:5000"
API_key = "593425E324D842BCB2938C7D8E583B76" #F691A0A08DE24F4F8DE536A2C9790E27 for bb465-test; 593425E324D842BCB2938C7D8E583B76 for local

@app.route('/', methods=['GET'])
def sample_status():
    os.environ["NO_PROXY"] = "127.0.0.1"
    tempTool = requests.get(f"http://{OctoPrint_instance}/api/printer/tool", headers={"X-Api-Key":API_key}, verify=False)
    tempBed = requests.get(f"http://{OctoPrint_instance}/api/printer/bed", headers={"X-Api-Key":API_key}, verify=False)
    statusflags = requests.get(f"http://{OctoPrint_instance}/api/printer?exclude=temperature,sd", headers={"X-Api-Key":API_key}, verify=False)

    #tool identifier
    tool = 'tool0'
    #converting tool request content to json
    toolData = tempTool.content
    toolData_json = json.loads(toolData)
    print(toolData_json)
    #access tool-specific request content
    toolData_select = toolData_json[tool]
    #access tool current & target temperatures
    toolData_current = toolData_select["actual"]
    toolData_target = toolData_select["target"]

    if toolData_current >= 60:
        toolData_safety = "NOT SAFE"
        toolData_safety_CSS = "danger"
    elif toolData_current < 60:
        toolData_safety = "SAFE"
        toolData_safety_CSS = "safe"

    #converting tool request content to json
    bedData = tempBed.content
    bedData_json = json.loads(bedData)
    #access tool-specific request content
    bedData_select = bedData_json["bed"]
    #access tool current & target temperatures
    bedData_current = bedData_select["actual"]
    bedData_target = bedData_select["target"]

    if bedData_current >= 60:
        bedData_safety = "NOT SAFE"
        bedData_safety_CSS = "danger"
    elif bedData_current < 60:
        bedData_safety = "SAFE"
        bedData_safety_CSS = "safe"

    statusData = statusflags.content
    print(str(statusData.decode()))

    printer_status = "Inactive"

    return render_template("inactive.html", status=printer_status, 
    tempTool_current = toolData_current, 
    tempTool_target = toolData_target, 
    toolStatus_safety = toolData_safety_CSS,
    toolStatus = toolData_safety,
    tempBed_current = bedData_current, 
    tempBed_target = bedData_target,
    bedStatus_safety = bedData_safety_CSS,
    bedStatus = bedData_safety)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5001, debug=True)





        
