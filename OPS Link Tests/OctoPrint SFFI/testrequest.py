import requests
import json

tempTool = requests.get("https://10.32.46.211/api/printer/tool", headers={"X-Api-Key":"F691A0A08DE24F4F8DE536A2C9790E27"}, verify=False)
tempBed = requests.get("https://10.32.46.211/api/printer/bed", headers={"X-Api-Key":"F691A0A08DE24F4F8DE536A2C9790E27"}, verify=False)
statusflags = requests.get("https://10.32.46.211/api/printer?exclude=temperature,sd", headers={"X-Api-Key":"F691A0A08DE24F4F8DE536A2C9790E27"}, verify=False)

#tool identifier
tool = 'tool0'
#converting tool request content to json
toolData = tempTool.content
toolData_json = json.loads(toolData)
#access tool-specific request content
toolData_select = toolData_json[tool]
#access tool current & target temperatures
toolData_current = toolData_select["actual"]
toolData_target = toolData_select["target"]

#converting tool request content to json
bedData = tempBed.content
bedData_json = json.loads(bedData)
#access tool-specific request content
bedData_select = bedData_json["bed"]
#access tool current & target temperatures
bedData_current = bedData_select["actual"]
bedData_target = bedData_select["target"]

printer_status = ""

statusData = statusflags.content
print(str(statusData.decode()))

