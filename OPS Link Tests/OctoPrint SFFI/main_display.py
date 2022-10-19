from math import floor
import requests 
import json
import os
import time
from flask import Flask, render_template, request, url_for
import concurrent.futures as cf
import datetime as dt

app=Flask(__name__)

OctoPrint_instance = "127.0.0.1:5000"

API_key = "593425E324D842BCB2938C7D8E583B76" #"60F9D39D7BED47E793A89BA01156B141" for ubuntu local #F691A0A08DE24F4F8DE536A2C9790E27 for bb465-test; 593425E324D842BCB2938C7D8E583B76 for local

prev_timeleft = ""
prev_tooltemp = ""
prev_bedtemp = ""

@app.route('/', methods=['GET', 'POST'])
def sample_status():
    
    os.environ["NO_PROXY"] = "127.0.0.1"
    try:
        tempTool = requests.get(f"http://{OctoPrint_instance}/api/printer/tool", headers={"X-Api-Key":API_key}, verify=False)
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

        toolData_safety = ""
        toolData_safety_CSS = ""

        if toolData_current >= 50:
            toolData_safety = "not safe"
        elif toolData_current < 50:
            toolData_safety = "safe"

        toolData_state = ""
        toolData_state_CSS = ""

        if toolData_current < toolData_target:
            toolData_state = "heating"
        elif toolData_current == toolData_target:
            toolData_state = "temp stable"
        elif toolData_current > toolData_target:
            toolData_state = "cooling"

        
        ##Bed Data##

        #tempBed (request object) refers to all printer bed temperature data
        #bedData is the raw response data for tempBed
        #bedData_json is bedData converted into json
        #bedData_select subsets bedData_json for all items under the "bed" json object
        #bedData_current is the current bed temperature (in degrees C)
        #bedData_target is the current target bed temperature (in degrees C)
        
        
        tempBed = requests.get(f"http://{OctoPrint_instance}/api/printer/bed", headers={"X-Api-Key":API_key}, verify=False)
            
        #converting tool request content to json
        bedData = tempBed.content
        bedData_json = json.loads(bedData)
        #access tool-specific request content
        bedData_select = bedData_json["bed"]
        #access tool current & target temperatures
        bedData_current = bedData_select["actual"]
        bedData_target = bedData_select["target"]

        bedData_safety = ""
        bedData_safety_CSS = ""

        if bedData_current >= 50:
            bedData_safety = "not safe"
        elif bedData_current < 50:
            bedData_safety = "safe"

        bedData_state = ""
        bedData_state_CSS = "" 

        if bedData_current < bedData_target:
            bedData_state = "heating"
        elif bedData_current == bedData_target:
            bedData_state = "temp stable"
        elif bedData_current > bedData_target and bedData_target == 0:
            if bedData_current >= 25:
                bedData_state = "cooling"
            else: 
                bedData_state = "temp stable"
        elif bedData_current > bedData_target and bedData_target != 0:
            bedData_state = "cooling"
        

        statusflags = requests.get(f"http://{OctoPrint_instance}/api/job", headers={"X-Api-Key":API_key}, verify=False)

        if toolData_current >= 60 or bedData_current >= 60:
            statusData = statusflags.content
            statusData_json = json.loads(statusData) #converts statusData to json
            statusData_progress = statusData_json["progress"] #accesses progress data in statusData

            statusData_timeleft = statusData_progress["printTimeLeft"]
            statusData_progress = statusData_json["progress"]
            statusData_completion = statusData_progress["completion"]

            print(statusData_json)
            
            if None in [statusData_timeleft, statusData_progress, statusData_completion]:
                statusData_timeleft = 0
                statusData_progress = 100
                statusData_completion = 100
                printer_status = "Stopped"

                return render_template("stopped.jinja2", status=printer_status, 
                    tempTool_current = toolData_current, 
                    tempTool_target = toolData_target,
                    toolStatus = toolData_safety,
                    toolState = toolData_state,
                    tempBed_current = bedData_current, 
                    tempBed_target = bedData_target,
                    bedStatus = bedData_safety,
                    bedState = bedData_state,
                    print_completion = str(statusData_completion))

            else: #Printer is actively printing/paused
                if floor(statusData_timeleft/3600) >= 1:
                    if floor(statusData_timeleft/3600) > 1:
                        statusData_timeleft_processed = f"{floor(float(statusData_timeleft)/3600)} hours"
                    else:
                        statusData_timeleft_processed = f"{floor(float(statusData_timeleft)/3600)} hour"
                elif statusData_timeleft/3600 <= 1 and floor(statusData_timeleft/60) > 1:
                    statusData_timeleft_processed = f"{floor(float(statusData_timeleft)/60)} minutes"
                elif statusData_timeleft/3600 <= 1 and floor(statusData_timeleft/60) == 1:
                    statusData_timeleft_processed = f"{floor(float(statusData_timeleft)/60)} minute"    
                elif statusData_timeleft/3600 <= 1 and statusData_timeleft/60 < 1:
                    statusData_timeleft_processed = "Less than a minute"     

                statusData_job = statusData_json["job"] 
                statusData_printstatus = statusData_json["state"]

                print(str(statusData.decode()))

                if statusData_printstatus == "Printing" or statusData_printstatus == "Operational":
                    if statusData_completion >= 0.05 and statusData_completion < 100:
                        printer_status = "Printing"
                    elif statusData_completion <= 0.05:
                        printer_status = "Starting"        
                    elif statusData_completion == 100 and statusData_printstatus == "Operational":
                        printer_status = "Complete"
                    else:
                        printer_status = "Inactive"

                    return render_template("printing.jinja2", status=printer_status, 
                        tempTool_current = toolData_current, 
                        tempTool_target = toolData_target,
                        toolStatus = toolData_safety,
                        toolState = toolData_state,
                        tempBed_current = bedData_current, 
                        tempBed_target = bedData_target,
                        bedStatus = bedData_safety,
                        bedState = bedData_state,
                        print_completion = str(statusData_completion),
                        print_timeleft = statusData_timeleft_processed)

                elif statusData_printstatus == "Paused" or statusData_printstatus == "Pausing":
                    printer_status = statusData_printstatus

                    return render_template("paused.jinja2", status=printer_status, 
                        tempTool_current = toolData_current, 
                        tempTool_target = toolData_target,
                        toolStatus = toolData_safety,
                        toolState = toolData_state,
                        tempBed_current = bedData_current, 
                        tempBed_target = bedData_target,
                        bedStatus = bedData_safety,
                        bedState = bedData_state,
                        print_completion = str(statusData_completion),
                        print_timeleft = statusData_timeleft_processed)
                else:
                    pass
                    
    
        else: 
            printer_status = "Inactive"

            return render_template("inactive.jinja2", status=printer_status, 
                tempTool_current = toolData_current, 
                tempTool_target = toolData_target,
                toolStatus = toolData_safety,
                toolState = toolData_state,
                tempBed_current = bedData_current, 
                tempBed_target = bedData_target,
                bedStatus = bedData_safety,
                bedState = bedData_state)
    except Exception:
        printer_status = "Offline"

        return render_template("offline.jinja2", status=printer_status)

    #tool identifier


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5001, debug=True)

