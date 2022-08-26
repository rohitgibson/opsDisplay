from __future__ import absolute_import, unicode_literals
from http import server

import os #allows (1) use of 127.0.0.1 for dev purposes && (2) integration of command line functions for future admin controls (to initiate OctoPrint updates, restarts, or shutdowns from the dashboard)
from threading import Event, Thread
import concurrent.futures as cf
from octoprint import events
import requests #essential for pushing data to server
import socket 

from octoprint.plugin import StartupPlugin, ShutdownPlugin, SettingsPlugin, TemplatePlugin, SimpleApiPlugin, EventHandlerPlugin
from octoprint.events import Events
import octoprint.printer
from octoprint.util import RepeatedTimer
from requests.models import InvalidURL

from . import plugin_config, requests_test

"""Start to follow the process at line """

class _connection_instance(RepeatedTimer):
    def __init__(self, server_endpoint, printer_id, access_key, current_ip):
        self._server_endpoint = "http://"+server_endpoint+"/printers/status/BB477-7"
        self._printer_uuid = printer_id
        self._server_api_key = access_key
        self._currentIP = current_ip
    
        self._session_context = None
        self._session_prepped = None
        self._session_endpoint = ""
        self._session_headers = {} #Unsure if this will be replaced with auth (will remove comment in future version)
        
        self._connection_status = None
        self._url_valid = None

        #requests_test is a self-developed test module providing mock requests endpoints & responses (with content & status code), allowing for dynamic responses to a variety of test scenarios
        self._requests = requests_test.Request() #creates a mock Request object -- based on requests.Request 
        self._requests.post("/api/eb04b454-e122-46f7-929b-d82687e83246") #Request.get based on requests.get

        self._connection_content = self._requests.content() #creates dummy content output for use later

        #FOR TEST PURPOSES
        __plugin_implementation__._logger.info(self._connection_content) 

    def _connection_init(self):
        __plugin_implementation__._logger.info("OCTOPRINTSERVER -- TESTING CONNECTION")

        #"NO_PROXY" only needed if connecting to localhost (for development purposes); brings in "connection_state" variable for modification
        os.environ['NO_PROXY'] = '127.0.0.1'
        connection_state = __plugin_implementation__._connection_state
        
        #Fundamental variables for session creation/context 
        self._session_endpoint = self._server_endpoint
        session_data = {"label":self._printer_uuid,"current_ip":self._currentIP,"msg_body":"OctoPrint active"}
        self._session_headers = {} #nOTE -> headers will be added with server-side pairing/api logic -- Basic HTTP Auth; format is "Server-API-Key":<API Key/password>
        
        #Creates "prepped" request
        try:
            session_init = requests.Request('POST', self._session_endpoint, headers=self._session_headers, data=session_data)
            session_prepped = session_init.prepare()
            self._url_valid = True
        except InvalidURL:
            __plugin_implementation__._logger.error("Unable to connect -- URL invalid")
            self._url_valid = False

        self._session_context = requests.Session()
        #Attempts connection with session context; only runs if URL is valid
        if self._url_valid is True:
            try:
                connection_attempt = self._session_context.send(session_prepped) 
                self._connection_status = connection_attempt.status_code
                self._connection_content = connection_attempt.content

                __plugin_implementation__._logger.info(self._connection_status)
            except Exception:
                self._connection_status = 0
                connection_state = 2
        else:
            pass
        
        #IF connection successful --> starts connection proper
        if self._connection_status == 200:   
            
            connection_state = 3
            __plugin_implementation__._logger.info("CONNECTION ESTABLISHED; PLUGIN ACTIVE")
            
            #timed "server alive" message start
            __plugin_implementation__._main_timer = RepeatedTimer(10, self._connection_keep, run_first=False, condition=__plugin_implementation__._check_timer)
            __plugin_implementation__._main_timer.start() 

            try:
                peer_endpoint = self._connection_content["peer_endpoint"]
                peer_access_key = self._connection_content["peer_api"]

                with cf.ThreadPoolExecutor(max_workers=2) as executor:
                    peer_one = executor.submit(__plugin_implementation__.peer_connection, peer_endpoint, peer_access_key)

            except Exception:
                __plugin_implementation__._logger.info("PEER CONNECTION FAILED -- Cannot connect to paired peer device")
                    
            
            #"Connection Instance" session details updated
            self._session_prepped = self._session_context.prepare_request(requests.Request('POST', self._session_endpoint, headers=self._session_headers))
        elif self._connection_status is not None and self._connection_status != 200:
            connection_state = 2
            __plugin_implementation__._logger.info("CONNECTION FAILED -- Cannot connect to server")
        else:
            pass

        #Reports "connection_state" output to main __plugin_implementation__ object
        __plugin_implementation__._connection_state = connection_state

    def _connection_keep(self):
        if __plugin_implementation__._connection_state != 1:
            self._connection_fire(self._printer_uuid, self._currentIP, 'heartbeat','Server alive')
        else:
            pass
        
    def _response_parse(self, response_content):
        server_state = response_content["state"]; printing_flag = server_state["printing"]; bed_clear_flag = server_state["bed_clear"]; isJobReady_flag = server_state["isJobReady"]

        __plugin_implementation__._logger.info(printing_flag)
    
    #Relies on existing persistent HTTP "session" -- pushes message to external API when called
    def _connection_fire(self, printer_id, printer_ip, message_type, data):
        
        #Based on "client direct" message -- see documentation
        output = {
        'message_origin':{
            'type': 'client_direct',
            'client_id': printer_id,
            'client_ip': printer_ip
        },
        'message':{
            'type':message_type,
            'data':data}
        }

        if __plugin_implementation__._connection_state != 1:
            try:
                self._requests.post(url="/api/eb04b454-e122-46f7-929b-d82687e83246", data=output)

                self._request_out = self._requests.content()
                self._response_parse(self._request_out)
                __plugin_implementation__._logger.info(f"Connection_event -- {message_type} -- POST success")

            except Exception:
                __plugin_implementation__._logger.info(f"Connection_event -- {message_type} -- POST failed")
        else: 
            pass

class octoprintServer(     
    StartupPlugin,     
    ShutdownPlugin,     
    EventHandlerPlugin,     
    SettingsPlugin,     
    TemplatePlugin,     
    SimpleApiPlugin   
    ):    
    #currentIP = "http://" + str(socket.gethostbyname(socket.gethostname())) + ":80"

    def __init__(self):
        self._server_endpoint = plugin_config.SERVER_ENDPOINT
        self._printer_id = plugin_config.PRINTER_ID
        self._access_key = plugin_config.ACCESS_KEY

        #Server connection variables
        self._currentIP = "http://" + str(socket.gethostbyname(socket.gethostname())) + ":80" #Need to test whether this works on OctoPrint (no reason it shouldn't)
        self._connection_state = 2 #1 = connection terminated; 2 = not connected; 3 = connection alive
        self._main_timer = None
        self._operation_state = False #True if "OPERATIONAL" event fired

    def data_validation(self):
        self._logger.info("Validating config...") #uses logging function within OctoPrint
        invalid_config_values = ["", None] 

        #Verifies plugin values are complete against the list of invalid config values (line 131)
        if plugin_config.SERVER_ENDPOINT in invalid_config_values or plugin_config.PRINTER_ID in invalid_config_values or plugin_config.ACCESS_KEY in invalid_config_values:
            self._logger.info("Config invalid -- missing one or more values")
            #Stops connection with existing config
        else:
            self._logger.info("Config valid -- starting plugin")
            #Attempts connection with existing config
            self._server_endpoint = plugin_config.SERVER_ENDPOINT; self._printer_id = plugin_config.PRINTER_ID; self._access_key = plugin_config.ACCESS_KEY
            self.plugin_init()
        
    def plugin_init(self):
        self._logger.info("Connection attempt started")
        
        #Three types of Connection States (all locally defined) -- (1) = Terminated; (2) = Inactive; (3) Operational
        if self._connection_state == 3:
            self._connection_kill(1) #Note that this doesn't work yet -- would likely only work if event fires could be self-contained within the connection class
        else:
            self._logger.info(f"Connecting to {self._server_endpoint}") 
            #Creates the self-contained connection object (for reasons that are hard to explain, we can't yet make this its own process thread -- see links in GitHub for more info)
            self._connection = _connection_instance(self._server_endpoint, self._printer_id, self._access_key, self._currentIP)
            self._connection._connection_init() #Triggers the start condition


            #EXPERIMENT -- sampling from own port
            os.environ['NO_PROXY'] = '127.0.0.1'
            willThisWork = requests.get("http://127.0.0.1:5000/api/printer", headers={"X-Api-Key":"593425E324D842BCB2938C7D8E583B76"})
            print(willThisWork.content)

    def on_after_startup(self):
        self._logger.info("Plugin started")
        self.data_validation() #Moves to line 129

    def get_api_commands(self):
        return dict(
            editconfig=["server_endpoint","printer_uuid","access_key"],
            connectReq=["server_endpoint"] #Inbound peer-to-peer connection requests
        )

    def on_api_command(self, command, data):
        if command == "editconfig":
            self._ping_data = data
            
            plugin_config.SERVER_ENDPOINT = self._ping_data["server_endpoint"]
            plugin_config.PRINTER_ID = self._ping_data["printer_uuid"]
            plugin_config.ACCESS_KEY = self._ping_data["access_key"]

            self.data_validation
        elif command == "connectReq":
            pass
        else:
            self._logger.info("Failed external command received")  

        repr(plugin_config)

    def _check_timer(self):
        #Whether timer is active (inactive if connection terminated)
        if self._connection_state != 1:
            return True
        else:
            return False

    def on_event(self, event, payload):
        event = event
        payload = payload
        try:
            if event in (Events.CONNECTED, Events.DISCONNECTED, Events.CLIENT_OPENED, Events.CLIENT_CLOSED, Events.PRINTER_STATE_CHANGED):
                __plugin_implementation__._connection._connection_fire(event,payload)

                #"error" event reporting
            elif event in (Events.ERROR):
                __plugin_implementation__._connection._connection_fire(event,payload)
            else:
                pass
        except AttributeError:
            pass

    def _connection_kill(self, reason):
        if reason == 1: #Connection restart (due to change in settings or *manual reset)
            self._connection_state = 2
            self._logger.info("CONNECTION RESTARTING")
        elif reason == 2: #Connection terminated 
            self._connection_state = 1
            self._logger.info("CONNECTION TERMINATED")


__plugin_identifier__ = "OPSlight"
__plugin_package__ = "OPSlight"
__plugin_name__ = "OctoPrintServer Light Client"
__plugin_version__ = "2021-05-D1"
__plugin_description__ = "OctoPrintServer (OPS) Light Client -- Lightweight client connecting printer to server and assigned cluster broker"
__plugin_author__ = "Rohit Gibson"
__plugin_author_email__ = "rgibso50@students.kennesaw.edu"
__plugin_pythoncompat__ = ">2.7,<4"
__plugin_implementation__ = octoprintServer()
__plugin_hooks__ = {}

