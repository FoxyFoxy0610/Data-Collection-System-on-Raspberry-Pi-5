#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' For hipnuc module '
import sys
# this specify path of pyserial
# sys.path.append("/usr/lib/python3/dist-packages")
import threading
import serial
import json
from queue import Queue
from CH_100.hipnuc_protocol import *
import time
import os

import binascii


class hipnuc_module(object):
    """
    Parameters
    ----------
    path_configjson : string, a path for config.json.

    """

    def __init__(self, path_configjson=None):

        def serialthread():
            while self.serthread_alive:
                # If the serial port has data, receive it into the buffer
                if self.serial.in_waiting:
                    # read serial port
                    data = self.serial.read(self.serial.in_waiting)
                    # put into buffer
                    self.binbuffer.extend(data)
                else:
                    pass

                # Parse buffer data
                try:
                    while True:
                        # try to find the complete frame, throw an exception if it fails
                        headerpos, endpos = intercept_one_complete_frame(
                            self.binbuffer)
                        # Parse the full frame
                        extraction_information_from_frame(
                            self.binbuffer[headerpos:endpos + 1], self.module_data_fifo, self.config["report_datatype"])
                        self.binbuffer = self.binbuffer[endpos + 1:]

                except HipnucFrame_NotCompleted_Exception as NotCompleted:
                    #Receive in progress
                    pass
                except HipnucFrame_ErrorFrame_Exception as e:
                    print(e)
                    # The current frame has a frame header, but it is an error frame, skip the error frame
                    headerpos = find_frameheader(self.binbuffer)
                    self.binbuffer = self.binbuffer[headerpos + 1:]
                finally:
                    pass

                # max achieve 1000Hz
                time.sleep(0.001)

        # Parse the json configuration file
        if path_configjson != None:
            # open configuration file
            config_json = open(path_configjson, 'r', encoding='utf-8')
            self.config = json.load(config_json)
            # close the configuration file
            config_json.close()
            # configure
            portx = self.config["port"]
            bps = self.config["baudrate"]
        else:
            pass

        # Initialize serial port
        # Open serial port and get serial port object
        self.serial = serial.Serial(portx, bps, timeout=None)
        # FIFO
        self.module_data_fifo = Queue()

        self.binbuffer = []

        self.serthread_alive = True
        self.serthread = threading.Thread(target=serialthread)
        self.serthread.start()

        self.sample_timer = None
        self.sample_timer = threading.Timer(
            1.00, sample_rate_timer_cb, args=(self.sample_timer,))
        self.sample_timer.start()

        self.frame_counter = 0
        self.csv_timestamp = 0

    def get_module_data(self, timeout=None):
        """retrieve data.

         Get received mod data.

         Parameters
         ------------
         timeout :
             Optional parameter. If it is None (the default value), it will block until there is a valid value;
             If the timeout is positive, it will try to wait for valid data and block for timeout seconds. If there is no valid data after the blocking time, an Empty exception will be thrown.

         Returns
         -------
         data : dict(key, value), value is list
             Returns the module data, the type is a dictionary

        """

        data = self.module_data_fifo.get(block=True, timeout=timeout)
        return data

    def get_module_data_size(self):
        """Get the number of data.

         Get the number of mod data received.
         Note: If the return length is greater than 0, it is not guaranteed that get_module_data will not be blocked.

         Parameters
         ------------
         none

         Returns
         -------
         size : int
             Returns the module data, the type is a dictionary

        """

        return self.module_data_fifo.qsize()

    def close(self):
        """Close the module.

         Turn off the specified mod.

         Parameters
         ------------
         none

         Returns
         -------
         none

        """
        self.serthread_alive = False
        sample_rate_timer_close()
        self.serial.close()

    def create_csv(self, filename="chlog.csv"):
        self.frame_counter = 0

        if os.path.exists(filename):
            os.remove(filename)
        f = open(filename, 'w')
        print('%s is created(overwritten).' % (filename))

        f.close()

    def write2csv(self, data, filename="chlog.csv"):

        f = open(filename, 'a')

        if 'GWD' in data.keys():
            # 0x62 protocol, log the data from Hi221 dongle
            nodes=data['nodes']

            if self.frame_counter == 0:
                csv_row_name = "frame,unix_timestamp"
                node_content=",ID,accX,accY,accZ,gyrX,gyrY,gyrZ,nagX,magY,magZ,eulX,eulY,eulZ,quatW,quatX,quatY,quatZ"
                for i in range(0,len(nodes.keys())):
                    csv_row_name+=node_content
                csv_row_name += '\n'
                f.write(csv_row_name)
                self.frame_counter += 1
            csv_row_value = "%d,%d," % (self.frame_counter,data['timestamp'])
            
            for node_id in nodes.keys():
                csv_row_value += node_id+','
                for sensor_type in nodes[node_id].keys():
                    for axis in nodes[node_id][sensor_type].keys():                        
                            value=nodes[node_id][sensor_type][axis]
                            csv_row_value += str(value)+','
                    
            csv_row_value += '\n'
            f.write(csv_row_value)
        else:
            if self.frame_counter == 0:
                csv_row_name = "frame,"
                for key, data_list in data.items():
                    for axis_dic in data_list:
                        for axis, value in axis_dic.items():

                            csv_row_name += key+axis+','
                csv_row_name += '\n'
                f.write(csv_row_name)
                self.frame_counter += 1

            csv_row_value = "%d," % (self.frame_counter)
            for data_list in data.values():
                for axis_dic in data_list:
                    for axis, value in axis_dic.items():
                        csv_row_value += str(value)+','

            csv_row_value += '\n'
            f.write(csv_row_value)

        f.close()
        self.frame_counter += 1

        #print ('writed %s:%d'%(filename,self.frame_counter))
