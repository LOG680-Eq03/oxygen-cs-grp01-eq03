import sys, os, time, json, requests, logging
from signalrcore.hub_connection_builder import HubConnectionBuilder
from dotenv import dotenv_values

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from database import DbConnect


class Main:
    def __init__(self):
        self._hub_connection = None
        self.TOKEN=None
        self.HOST="http://34.95.34.5"
        self.TICKETS=5
        self.T_MAX=100
        self.T_MIN=0
        self.DATABASE=None

    def __del__(self, *args, **kwargs):
        if self._hub_connection is not None:
            self._hub_connection.stop()

    def __checkTokenVariable__(self):
        if self.TOKEN is None:
            raise Exception(
                "Tickets variable not setup (you need .env file or pass throught arguments)"
            )

    def __initFromArgs__(self, *args):
        for arg in args:
            vals = arg.split("=")
            self.__addVariable__(vals[0], vals[1])

    def __initFromEnvFile__(self, **kwargs):
        for k, v in kwargs.items():
            self.__addVariable__(k, v)

    def __addVariable__(self, name, value):
        if hasattr(self, name):
            setattr(self, name, value)

    def setup(self, *args):
        directory = os.getcwd()
        env_path = os.path.join(directory, ".env")
        kwargs = {}
        if os.path.isfile(env_path):
            kwargs = dotenv_values(dotenv_path=env_path)
        if len(args) == 0 and len(kwargs) == 0:
            raise Exception("no environment variable was given")
        if len(kwargs)  > 0:
            self.__initFromEnvFile__(**kwargs)
        if len(args) > 0:
            self.__initFromArgs__(*args)
        self.__checkTokenVariable__()
        if self.DATABASE is not None:
            self.DATABASE = DbConnect(self.DATABASE)
        else:
            print("WARNING !! no database was found, data will only display")
        self.setSensorHub()

    def start(self, *args):
        self.setup(*args)
        self._hub_connection.start()

        print("Press CTRL+C to exit.")
        while True:
            time.sleep(2)

    def setSensorHub(self):
        self._hub_connection = (
            HubConnectionBuilder()
            .with_url(f"{self.HOST}/SensorHub?token={self.TOKEN}")
            .configure_logging(logging.INFO)
            .with_automatic_reconnect(
                {
                    "type": "raw",
                    "keep_alive_interval": 10,
                    "reconnect_interval": 5,
                    "max_attempts": 999,
                }
            )
            .build()
        )

        self._hub_connection.on("ReceiveSensorData", self.onSensorDataReceived)
        self._hub_connection.on_open(lambda: print("||| Connection opened."))
        self._hub_connection.on_close(lambda: print("||| Connection closed."))
        self._hub_connection.on_error(
            lambda data: print(f"||| An exception was thrown closed: {data.error}")
            )

    def onSensorDataReceived(self, data):
        try:
            print(data[0]["date"] + " --> " + data[0]["data"])
            date = data[0]["date"]
            dp = float(data[0]["data"])
            if self.DATABASE is not None:
                self.send_event_to_database(date, dp)
            self.analyzeDatapoint(date, dp)
        except Exception as err:
            print(err)

    def analyzeDatapoint(self, date, data):
        if float(data) >= float(self.T_MAX):
            self.sendActionToHvac(date, "TurnOnAc", self.TICKETS)
        elif float(data) <= float(self.T_MIN):
            self.sendActionToHvac(date, "TurnOnHeater", self.TICKETS)

    def sendActionToHvac(self, date, action, nbTick):
        req_sim = requests.get(f"{self.HOST}/api/hvac/{self.TOKEN}/{action}/{nbTick}")
        details = json.loads(req_sim.text)
        print(date + " --> " + details['Response'])

    def send_event_to_database(self, timestamp, event):
        try:
            self.DATABASE.insertDb(timestamp, event)
            pass
        except requests.exceptions.RequestException as error_request:
            print(error_request.response)
            exit(1)

if __name__ == "__main__":
    args = sys.argv[1:]
    main = Main()
    main.start(*args)
