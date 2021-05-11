import json
import requests
import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from datetime import timedelta
from datetime import datetime

from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
from homeassistant.components.sensor import PLATFORM_SCHEMA

# Frequency of data retrieval (API allows for a maximum of 10times / minute)
MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=5)

CONF_NAME = "name"
CONF_API_KEY = "api_key"
CONF_SN = "sn"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_API_KEY): cv.string,
        vol.Required(CONF_SN): cv.string
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    solax_cloud = SolaxCloud(
        hass, config[CONF_NAME], config[CONF_API_KEY], config[CONF_SN])
    add_entities([InverterTotalYieldSensor(hass, solax_cloud),
                  InverterDailyYieldSensor(hass, solax_cloud),
                  InverterACPowerSensor(hass, solax_cloud)
                  ], True)


class SolaxCloud:
    def __init__(self, hass, name, api_key, sn):
        self.hass = hass
        self.logger = logging.getLogger(__name__)
        self.api_key = api_key
        self.sn = sn
        self.inverter_name = name
        self.data = {}
        self.uri = f'https://www.solaxcloud.com:9443/proxy/api/getRealtimeInfo.do?tokenId={api_key}&sn={sn}'
        self.last_data_time = None

    def get_data(self):
        if not self.data or datetime.now() - self.last_data_time > MIN_TIME_BETWEEN_UPDATES:
            try:
                data = requests.get(self.uri).json()
                if data['success'] == True:
                    self.data = data['result']
                    self.last_data_time = datetime.now()
                    self.logger.info(
                        f'Retrieved new data from solax cloud {self.inverter_name}')
                else:
                    self.data = {}
                    self.logger.error(data['exception'])
            except requests.exceptions.ConnectionError as e:
                self.logger.error(str(e))
                self.data = {}

# Inverter.AC.power.total
class ACPowerSensor(Entity):
    def __init__(self, hass, solax_cloud):
        self._name = solax_cloud.inverter_name + ' AC Power'
        self.hass = hass
        self.solax_cloud = solax_cloud

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        data = self.solax_cloud.data.get('acpower')
        return float('nan') if data is None else data

    @property
    def unit_of_measurement(self):
        return 'W'

    @property
    def icon(self):
        return 'mdi:solar-power'

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        self.solax_cloud.get_data()

#Inverter.AC.energy.out.daily
class YieldTodaySensor(Entity):
    def __init__(self, hass, solax_cloud):
        self._name = solax_cloud.inverter_name + ' Daily yield'
        self.hass = hass
        self.solax_cloud = solax_cloud

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        data = self.solax_cloud.data.get('yieldtoday')
        return float('nan') if data is None else data

    @property
    def unit_of_measurement(self):
        return 'kWh'

    @property
    def icon(self):
        return 'mdi:solar-power'

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        self.solax_cloud.get_data()

#Inverter.AC.energy.out.total
class YieldTotalSensor(Entity):
    def __init__(self, hass, solax_cloud):
        self._name = solax_cloud.inverter_name + ' Total yield'
        self.hass = hass
        self.solax_cloud = solax_cloud

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        data = self.solax_cloud.data.get('yieldtotal')
        return float('nan') if data is None else data

    @property
    def unit_of_measurement(self):
        return 'kWh'

    @property
    def icon(self):
        return 'mdi:solar-power'

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        self.solax_cloud.get_data()

#Grid.power.total
class FeedinPowerSensor(Entity):
    def __init__(self, hass, solax_cloud):
        self._name = solax_cloud.inverter_name + ' Grid power total'
        self.hass = hass
        self.solax_cloud = solax_cloud

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        data = self.solax_cloud.data.get('feedinpower')
        return float('nan') if data is None else data

    @property
    def unit_of_measurement(self):
        return 'W'

    @property
    def icon(self):
        return 'mdi:transmission-tower'

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        self.solax_cloud.get_data()

#Grid.energy.toGrid.total
class FeedinEnergySensor(Entity):
    def __init__(self, hass, solax_cloud):
        self._name = solax_cloud.inverter_name + ' To grid yield'
        self.hass = hass
        self.solax_cloud = solax_cloud

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        data = self.solax_cloud.data.get('feedinenergy')
        return float('nan') if data is None else data

    @property
    def unit_of_measurement(self):
        return 'kWh'

    @property
    def icon(self):
        return 'mdi:transmission-tower'

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        self.solax_cloud.get_data()

#Grod/energy.fromGrid.total
class ConsumeEnergySensor(Entity):
    def __init__(self, hass, solax_cloud):
        self._name = solax_cloud.inverter_name + ' From grid yield'
        self.hass = hass
        self.solax_cloud = solax_cloud

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        data = self.solax_cloud.data.get('consumeenergy')
        return float('nan') if data is None else data

    @property
    def unit_of_measurement(self):
        return 'kWh'

    @property
    def icon(self):
        return 'mdi:transmission-tower'

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        self.solax_cloud.get_data()

#Inverter.Meter2.AC.power.total
class FeedinPowerM2Sensor(Entity):
    def __init__(self, hass, solax_cloud):
        self._name = solax_cloud.inverter_name + ' AC power'
        self.hass = hass
        self.solax_cloud = solax_cloud

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        data = self.solax_cloud.data.get('feedinpowerM2')
        return float('nan') if data is None else data

    @property
    def unit_of_measurement(self):
        return 'W'

    @property
    def icon(self):
        return 'mdi:solar-power'

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        self.solax_cloud.get_data()

#BMS.energy.SOC
class SocSensor(Entity):
    def __init__(self, hass, solax_cloud):
        self._name = solax_cloud.inverter_name + ' State of charge'
        self.hass = hass
        self.solax_cloud = solax_cloud

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        data = self.solax_cloud.data.get('soc')
        return float('nan') if data is None else data

    @property
    def unit_of_measurement(self):
        return '%'

    @property
    def icon(self):
        return 'mdi:battery'

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        self.solax_cloud.get_data()

#Inverter.AC.EPS.power.R
class Peps1Sensor(Entity):
    def __init__(self, hass, solax_cloud):
        self._name = solax_cloud.inverter_name + ' ESP R'
        self.hass = hass
        self.solax_cloud = solax_cloud

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        data = self.solax_cloud.data.get('peps1')
        return float('nan') if data is None else data

    @property
    def unit_of_measurement(self):
        return 'W'

    @property
    def icon(self):
        return 'mdi:solar-power'

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        self.solax_cloud.get_data()

#Inverter.AC.EPS.power.S
class Peps2Sensor(Entity):
    def __init__(self, hass, solax_cloud):
        self._name = solax_cloud.inverter_name + ' ESP S'
        self.hass = hass
        self.solax_cloud = solax_cloud

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        data = self.solax_cloud.data.get('peps2')
        return float('nan') if data is None else data

    @property
    def unit_of_measurement(self):
        return 'W'

    @property
    def icon(self):
        return 'mdi:solar-power'

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        self.solax_cloud.get_data()

#Inverter.AC.EPS.power.T
class Peps3Sensor(Entity):
    def __init__(self, hass, solax_cloud):
        self._name = solax_cloud.inverter_name + ' ESP T'
        self.hass = hass
        self.solax_cloud = solax_cloud

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        data = self.solax_cloud.data.get('peps3')
        return float('nan') if data is None else data

    @property
    def unit_of_measurement(self):
        return '%'

    @property
    def icon(self):
        return 'mdi:solar-power'

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        self.solax_cloud.get_data()

#Inverter type (Table 4)
# TODO: Add sensor

#Inverter status (Table 5)
# TODO: Add sensor

#Update time (Table 5)
# TODO: Add sensor

#Inverter.DC.Battery.power.total
class BatPowerSensor(Entity):
    def __init__(self, hass, solax_cloud):
        self._name = solax_cloud.inverter_name + ' Battery power'
        self.hass = hass
        self.solax_cloud = solax_cloud

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        data = self.solax_cloud.data.get('batpower')
        return float('nan') if data is None else data

    @property
    def unit_of_measurement(self):
        return 'W'

    @property
    def icon(self):
        return 'mdi:battery'

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        self.solax_cloud.get_data()

#Inverter.DC.PV.power.MPPT1
class PowerDC1Sensor(Entity):
    def __init__(self, hass, solax_cloud):
        self._name = solax_cloud.inverter_name + ' MPPT 1'
        self.hass = hass
        self.solax_cloud = solax_cloud

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        data = self.solax_cloud.data.get('powerdc1')
        return float('nan') if data is None else data

    @property
    def unit_of_measurement(self):
        return 'W'

    @property
    def icon(self):
        return 'mdi:solar-power'

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        self.solax_cloud.get_data()

#Inverter.DC.PV.power.MPPT2
class PowerDC2Sensor(Entity):
    def __init__(self, hass, solax_cloud):
        self._name = solax_cloud.inverter_name + ' MPPT 2'
        self.hass = hass
        self.solax_cloud = solax_cloud

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        data = self.solax_cloud.data.get('powerdc2')
        return float('nan') if data is None else data

    @property
    def unit_of_measurement(self):
        return 'W'

    @property
    def icon(self):
        return 'mdi:solar-power'

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        self.solax_cloud.get_data()
