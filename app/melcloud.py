import requests
import logging
import json
from prometheus_client import Gauge



class MelcloudController:

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.device_id = None
        self.location_id = None
        self.session = requests.Session()
        self.url = 'https://app.melcloud.com/Mitsubishi.Wifi.Client'
        self.context_id = None

        self.effectiveflags = None
        self.settemprature = None
        self.fanspeed = None
        self.roomtemprature = None
        self.operation_mode = None
        self.vanevertical = None
        self.has_power = None

        self.number_of_fanspeeds = 5

        self.roomtempraturegauge = Gauge('mellib_roomtemprature', 'Room Temprature')
        self.fanspeedgauge = Gauge('mellib_fanspeed', 'Fan Speed')
        self.settempraturegauge = Gauge('mellab_settemprature', 'Temprature Target')
        self.has_powergaugegauge = Gauge('melcloud_has_power', "Power Status")
        self.operation_modegauge = Gauge('mellib_operation_mode', "Running Operation Mode")

        # Konfigurer logging
        self.logger = logging.getLogger('MelcloudController')
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Logger til konsoll
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        if not self.context_id:
            self.login()

        if not self.device_id:
            self.set_ids()

        if not self.roomtemprature:
            self.update_device_data()





    def login(self):
        login_url = '%s/Login/ClientLogin' % self.url
        payload = {
            'Email': self.username,
            'Password': self.password,
            'AppVersion': "1.26.2.0",
            'Language': '13'
        }
        response = self.session.post(login_url, json=payload)
        if response.ok:
            data = response.json()

            self.context_id = data['LoginData']['ContextKey']
            self.logger.debug('CONTEXTID:%s' % self.context_id)
            self.logger.info('Innlogging vellykket.')
            return True
        else:
            self.logger.error('Innlogging mislyktes. Sjekk dine innloggingsdetaljer.')
            return False

    def set_ids(self):
        url ='%s/User/ListDevices' % self.url
        headers = {
            'X-MitsContextKey': self.context_id
        }
        res = self.session.get(url=url, headers=headers)

        j = json.loads(res.text)

        self.device_id = j[0]['Structure']['Devices'][0]['DeviceID']
        self.location_id = j[0]['Structure']['Devices'][0]['BuildingID']

        self.logger.info(f"Device ID: {self.device_id}")
        self.logger.info(f"Location ID: {self.location_id}")




    def get_device(self):
        get_device_url = f'%s/Device/Get?id=%s&buildingID=%s' \
                         % (self.url,self.device_id, self.location_id)
        headers = {
            'X-MitsContextKey': self.context_id
        }

        response = self.session.get(get_device_url, headers=headers)

        if response.ok:
            data = response.json()
            return data

        else:
            self.logger.error('DEBUGDATA: %s' % response.status_code)
            self.logger.error('Kunne ikke hente enhetsinfo')

    def update_device_data(self):
        data = self.get_device()

        if data:
            self.roomtemprature = data['RoomTemperature']
            self.settemprature = data['SetTemperature']
            self.fanspeed = data['SetFanSpeed']
            self.operation_mode = data['OperationMode']
            self.vanevertical = data['VaneVertical']
            self.vanehorizontal = data['VaneHorizontal']
            self.has_power = data['Power']

            self.roomtempraturegauge.set(self.roomtemprature)
            self.fanspeedgauge.set(self.fanspeed)
            self.settempraturegauge.set(self.settemprature)
            self.has_powergaugegauge.set(self.has_power)
            self.operation_modegauge.set(self.operation_mode)

            self.logger.debug('Følgende variabeler er satt: %s, %s, %s, %s, %s, %s' % (self.roomtemprature, self.fanspeed,
                                                                                    self.operation_mode, self.vanevertical,
                                                                                    self.vanehorizontal, self.has_power))
            return True
        else:
            self.logger.error('Greide ikke å hente oppdaterte data')
            return False

    def create_json(self):
        j = {"EffectiveFlags": self.effectiveflags,
               "LocalIPAddress": None,
               "RoomTemperature": self.roomtemprature,
               "SetTemperature": self.settemprature,
               "SetFanSpeed": self.fanspeed,
               "OperationMode": self.operation_mode,
               "VaneHorizontal": self.vanehorizontal,
               "VaneVertical": self.vanevertical,
               "Name": None,
               "NumberOfFanSpeeds": 5,
               "Power": self.has_power,
                "DeviceID": self.device_id
               }

        return j

    def power(self, turnoff=False):
        set_power_url = f'https://app.melcloud.com/Mitsubishi.Wifi.Client/Device/SetAta'
        header = {
            'X-MitsContextKey': self.context_id,
        }

        j = self.create_json()

        if turnoff is False:
            j['Power'] = False
            j['EffectiveFlags'] = 1

        else:
            j['Power'] = True
            j['EffectiveFlags'] = 1


        self.logger.debug('Konvertert body: %s' % j)
        response = self.session.post(set_power_url, headers=header, json=j)
        data = response.status_code
        self.logger.debug('power-off command json response: %s' % data)
        self.update_device_data()

        return j

    def set_fan_speed(self, fan_speed):
        set_fan_speed_url = f'https://app.melcloud.com/Mitsubishi.Wifi.Client/Device/SetAta'
        headers = {
            'X-MitsContextKey': self.context_id
        }

        j = self.create_json()
        j['EffectiveFlags'] = 8
        j['SetFanSpeed'] = fan_speed

        response = self.session.post(set_fan_speed_url, headers=headers, json=j)
        data = response.json()
        self.logger.debug('Headers for response: %s ' % response.headers)
        self.logger.debug('json response %s' % data)

        if response.ok:
            self.logger.info(f'Satt viftehastighet til {fan_speed}.')
            self.update_device_data()

            return j
        else:
            self.logger.error(f'Feilet i å sette viftehastighet til {fan_speed}.')

    def set_temperature(self, temperature):
        set_temp_url = f'https://app.melcloud.com/Mitsubishi.Wifi.Client/Device/SetAta'
        headers = {
            'X-MitsContextKey': self.context_id
        }
        j = self.create_json()
        j['EffectiveFlags'] = 4
        j['SetTemperature'] = temperature

        response = self.session.post(set_temp_url, headers=headers, json=j)
        data = response.json()
        self.logger.info(data)

        if response.ok:
            self.logger.info(f'Satt temperatur til {temperature}°C.')
            self.update_device_data()

            return j

        else:
            self.logger.error(f'Feilet i å sette temperatur til {temperature}°C.')
            return False

    def set_operation_mode(self, operation_mode):
        set_temp_url = f'https://app.melcloud.com/Mitsubishi.Wifi.Client/Device/SetAta'
        headers = {
            'X-MitsContextKey': self.context_id
        }

        j = self.create_json()
        j['EffectiveFlags'] = 2

        if operation_mode is 1:
            self.logger.info('Turns on heating')
            j['OperationMode'] = 1

        elif operation_mode is 2:
            self.logger.info('Turn on drying')
            j['OperationMode'] = 2

        elif operation_mode is 3:
            self.logger.info('Turns on Air Condition')
            j['OperationMode'] = 3

        elif operation_mode is 8:
            self.logger.info('Turns on Auto-mode')
            j['OperationMode'] = 8

        response = self.session.post(set_temp_url, headers=headers, json=j)
        data = response.json()
        self.logger.info(data)

        if response.ok:
            self.logger.info(f'Operation Mode changed')
            self.update_device_data()

            return j

        else:
            self.logger.error(f'Operation Mode change failed')
            return {'errors': 'Operation Mode change failed'}


