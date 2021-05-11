# SolaxCloud integration for Home Assistant.

Solax Cloud integration based on the (now publicly accssible) SolaxCloud API.
This component is basically a rewrite of [thomascys/solaxcloud](https://github.com/thomascys/solaxcloud) which used the old system.
You need:

- The API Key which is accessible in the Service menu of your SolaxCloud.
- The Inverter Serial Number (SN) is the 10 character Registration No. of the
  specific inverter (see the Inverter's menu in SolaxCloud)

## Installation

- Place this directory in `/config/custom_components`. If `custom_components`
  does not exist, you have to create it.
- Add the sensor to your configuration.yaml:
```yaml
sensor:
  - platform: solaxcloud
    name: Inverter 1
    api_key: YOUR_API_KEY
    sn: YOUR_INVERTER_SN
```
- Verify that the custom entities are available in home assistant (Total Yield,
  Daily Yield and AC Power etc).

## Multiple Inverters

You might have multiple inverters in your PV installation. By simply adding the
same configuration again, but changing the inverter SN, you can add more
inverters to home assistant. Also, you might want a combined value of your
inverters, this can be achieved with home assistants template platform

```yaml
sensor:
  # ...
  - platform: solaxcloud
    name: Inverter 2
    api_key: YOUR_API_KEY
    sn: YOUR_INVERTER_2_SN

  - platform: template
    sensors:
      total_yield:
        friendly_name: 'Total Yield'
        icon_template: 'mdi:solar-power'
        unit_of_measurement: 'kWh'
        value_template: "{{ states('sensor.inverter_1.total_yield')|float + states('sensor.inverter_2.total_yield')|float }}"

      daily_yield:
        friendly_name: 'Daily Yield'
        icon_template: 'mdi:solar-power'
        unit_of_measurement: 'kWh'
        value_template: "{{ states('sensor.inverter_1.daily_yield')|float + states('sensor.inverter_2.daily_yield')|float }}"

      ac_power:
        friendly_name: 'AC Power'
        icon_template: 'mdi:solar-power'
        unit_of_measurement: 'kW'
        value_template: "{{ states('sensor.inverter_1.ac_power')|float + states('sensor.inverter_2.ac_power')|float }}"
```
