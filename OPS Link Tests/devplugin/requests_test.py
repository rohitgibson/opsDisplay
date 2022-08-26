import random
import uuid
import json

_uuid_printer_one = str(uuid.uuid4())
_uuid_printer_two = str(uuid.uuid4())
_uuid_printer_three = str(uuid.uuid4())

printer_id = "id"
current_ip = "127.0.0.1"

"""
SCENARIO ONE -- NO active print; NO queued job/file
--> "printing" = False
--> "bed_clear" = True
--> "isJobReady" = True
"""

_scen_one = {
    "printer":{
        "printer_id": printer_id,
        "printer_name": "Test Scenario 1",
        "current_ip": current_ip},
    "state":{
        "printing": False,
        "bed_clear": True,
        "isJobReady": True}
    }

"""
SCENARIO TWO -- ACTIVE print; NO queued job/file
--> "printing" = True
--> "bed_clear" = False
--> "isJobReady" = False
"""

_scen_two = {
    "printer":{
        "printer_id": printer_id,
        "printer_name": "Test Scenario 1",
        "current_ip": current_ip},
    "state":{
        "printing": True,
        "bed_clear": False,
        "isJobReady": False}
    }

"""
SCENARIO THREE -- ACTIVE print; QUEUED job/file
--> "printing" = True
--> "bed_clear" = False
--> "isJobReady" = True
"""

_scen_three = {
    "printer":{
        "printer_id": printer_id,
        "printer_name": "Test Scenario 1",
        "current_ip": current_ip},
    "state":{
        "printing": True,
        "bed_clear": False,
        "isJobReady": True}
    }

content = ""
status_code = ""

#_scenario_select = random.randint(1,3)

class Request:
    def post(self, url, *data, **headers):

        printer_id = "id"
        current_ip = "127.0.0.1"
        
        _scenario_select = 2 #random.randint(1,3)
        if url == "/api/eb04b454-e122-46f7-929b-d82687e83246":
            if _scenario_select == 1:
                self._content = _scen_one
            if _scenario_select == 2:
                self._content = _scen_two
            if _scenario_select == 3:
                self._content = _scen_three
            
            self._status_code = "200"
        else:
            self._content = ""
            self._status_code = "500"

    def get(self, url, *headers, **data):

        printer_id = "id"
        current_ip = "127.0.0.1"
        _scenario_select = 2 #random.randint(1,3)
        if url == "/api/eb04b454-e122-46f7-929b-d82687e83246":
            if _scenario_select == 1:
                self._content = _scen_one
            if _scenario_select == 2:
                self._content = _scen_two
            if _scenario_select == 3:
                self._content = _scen_three
            
            self._status_code = "200"
        else:
            self._content = ""
            self._status_code = "500"

    def content(self):
        return self._content

    def status_code(self):
        return self._status_code
