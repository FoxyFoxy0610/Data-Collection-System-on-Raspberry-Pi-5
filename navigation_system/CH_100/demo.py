#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from hipnuc_module import *
import traceback

log_file = 'chlog.csv'

if __name__ == '__main__':

    m_IMU = hipnuc_module('./config.json')
    print("Press Ctrl-C to terminate while statement.")

    #uncomment following line to enable csv logger
    m_IMU.create_csv(log_file) #uncomment this line to enable
    
    while True:
        try:
            data = m_IMU.get_module_data(10)
            
            #uncomment following line to enable csv logger
            m_IMU.write2csv(data, log_file)           
            
            print(data) #print all          

        except KeyboardInterrupt:            
            m_IMU.close()
            print("Serial is closed.")
            break  
        except Exception:
            print(traceback.format_exc())
            # or
            print(sys.exc_info()[2])
            pass