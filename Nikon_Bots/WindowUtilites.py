from Py4GWCoreLib import *
from datetime import datetime

#### --- LOGGING ROUTINE --- ####
## LogItem (text, Py4Gw.Console.MessageType)
class LogItem:
    """
        LogItem - Log window list item.
        text    - (str) text to show in log window, with timestamp optional
        msgType - (Py4GW.Console.MessageType) message type, changes color Info == White, Error == Red
    """
    def __init__(self, text, msgType):
        self.text = text
        self.msgType = msgType

## LogWindow (optional List[LogItem])
class LogWindow:
    """
        Log Window for adding logs and showing the output section.

        Function:
        Log - (str)(LogItem) log to add, text or LogItem instance.
        Log - (str)(Py4GW.Console.MessageType) log text to add with optional message type.
        DrawWindow - (void) Draws the child window section, enumerating all LogItems showing them sorted by order of add (descending)
    """
    output = []

    def AddLogs(self, logs):
        if type(logs) == list:
            for _, log in enumerate(logs):
                self.Log(log)
                if type(log) == LogItem:
                    self.Log(log)
                elif type(log) == str:
                    self.Log(log, Py4Gw.Console.MessageType.Info)
    def ClearLog(self):
        if self.output:
                self.output.clear()

    # check type of log, append or create LogItem
    def Log(self, logItem):
        if type(logItem) == LogItem:
            self.output.insert(0, logItem)
        elif type(logItem) == str:
            self.Log(logItem, Py4GW.Console.MessageType.Info)

    # create a new LogItem from string and apply message type.
    def Log(self, text, msgType):
        now = datetime.now()
        log_now = now.strftime("%H:%M:%S")
        text = f"[{log_now}] {text}"
        logItem = LogItem(text, msgType)
        self.output.insert(0, logItem)

    # Must be called from within a PyImGui.being()
    def DrawWindow(self):
        PyImGui.text("Logs:")
        PyImGui.begin_child("OutputLog", size=[0.0, -60.0], flags=PyImGui.WindowFlags.HorizontalScrollbar)        
        for _, logg in enumerate(self.output):
            if logg.msgType == Py4GW.Console.MessageType.Info:
                PyImGui.text(logg.text)
            elif logg.msgType == Py4GW.Console.MessageType.Warning:
                PyImGui.text_colored(logg.text, [1, 1, 0, 1])
            else:
                PyImGui.text_colored(logg.text, [1 ,0, 0, 1])
        PyImGui.end_child()
        
        if PyImGui.button("Clear"):            
            self.ClearLog()
#### --- LOGGING ROUTINE --- ####

#### --- BASIC WINDOW --- ####
class BasicWindow:
    name = "Basic Window"
    size = [300.0, 400.0]
    showLogger = True
    showState = True
    script_running = False
    script_status = "Stopped"
    current_state = "Idle"
    Logger = LogWindow()

    def __init__(self, window_name="Basic Window", window_size = [300.0, 400.0], show_logger = True, show_state = True):
        self.name = window_name
        self.size = window_size
        self.showLogger = show_logger
        self.showState = show_state
    
    def Show(self):
        # Start Basic Window
        PyImGui.begin(self.name, False, int(PyImGui.WindowFlags.AlwaysAutoResize))        
    
        # Start Main Content
        PyImGui.begin_child("Main Content", self.size, False, int(PyImGui.WindowFlags.AlwaysAutoResize))
        
        # Show the basic controls, this is the function to override for various selections
        self.ShowControls()

        # Show the output log along the bottom always if enabled
        if self.showLogger:
            PyImGui.separator()
            self.Logger.DrawWindow()

        # Show current state of bot (e.g. Started, Outpost, Dungeon, Stopped) if enabled after logs.
        if self.showState:
            PyImGui.separator()
            PyImGui.text(f"Status: {self.script_status} \t|\t State: {self.current_state}")

        # End MAIN child.        
        PyImGui.end_child()

        # End Basic Window
        PyImGui.end()
        
    def UpdateStatus(self, newStatus):
        self.script_status = newStatus

    def UpdateState(self, newState):
        self.current_state = newState

    def SetIdleState(self):
        self.script_running = False
        self.current_state = "Idle"

    '''
    *   Override in extended classes to customize controls on window.
    '''
    def ShowControls(self):
        PyImGui.text("-Bot Controls-")

        if PyImGui.button("Start"):
            self.StartBot()
            
        if PyImGui.button("Stop"):
            self.StopBot()

    def StartBot(self):
        self.script_running = True
        self.UpdateStatus("Running")
        self.Log("Bot Started")

    def StopBot(self):
        self.script_running = False
        self.UpdateStatus("Stopped")
        self.Log("Bot Stopped")

    def ResetBot(self):
        self.SetIdleState()
        self.UpdateStatus("Stopped")
        self.Log("Bot Forced Reset")

    def IsBotRunning(self):
        return self.script_running == True
    
    def ClearLog(self):
        if self.Logger:
            self.Logger.ClearLog()
            
    def Log(self, logItem):
        if self.Logger:
           self.Logger.Log(logItem)
           
    def Log(self, text, msgType=Py4GW.Console.MessageType.Info):
        if self.Logger:
           self.Logger.Log(text, msgType)
    
#### --- BASIC WINDOW --- ####