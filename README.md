# fae-bot
Software to control the FAE (Farming Automation Expriment) suspended robot. Pictures and hardware informations on http://fae-bot.org


## Intent

The goal of the FAE project is to bring a suspended platform to production for use by researchers and hobbyists in both robotics and agriculture. In order to be easily customizable and repairable, it uses popular and easy to obtained elements.

The embedded system is based on Raspberry Pi and Arduino. This repository contains the code for these two boards.

## Python code

The python code is inteded to be run on the two raspberry pis: one in the central command unit and one in the claw tool. It uses flask to serve an HTML UI and pyserial to send commands to the arduinos.

## Arduino code

In order to provide reliable timing and 5V signals, a basic arduino is connected through USB to the raspberry pi. It receives moving instructions through 56K serial and outputs impulses toward the motor drivers.

At the present stage of development, the information sent to the arduino is low level (refering to the motors individually) but we may at a later point do a proper G-code interface.
