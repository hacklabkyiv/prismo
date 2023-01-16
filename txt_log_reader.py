from flask import render_template, request
import os

log_file_mill  = "/home/pi/toolsmonitor/logs/mill.txt"
log_file_lathe = "/home/pi/toolsmonitor/logs/lathelog.txt"
log_file_laser = "/home/pi/toolsmonitor/logs/laserlog.txt"
log_file_cnc   = "/home/pi/toolsmonitor/logs/cnclog.txt"
log_file_b_cnc = "/home/pi/toolsmonitor/logs/bigcnclog.txt"
log_file_b_saw = "./device_logs/bandsawlog.txt"

def render_logs_to_html():
    equipment = request.args.get("equipment")
    
    if   equipment == "mill":
            log_file = log_file_mill
    elif equipment == "lathe":
            log_file = log_file_lathe
    elif equipment == "laser":
            log_file = log_file_laser
    elif equipment == "cnc":
            log_file = log_file_cnc
    elif equipment == "big_cnc":
            log_file = log_file_b_cnc
    elif equipment == "band_saw":
            log_file = log_file_b_saw
    else:
            # show mill logs by default
            log_file = log_file_mill
            equipment = "mill"
    
    log_records = read_log_file(log_file)
    
    return render_template("log_viewer.html", log_records=log_records, equipment=equipment)

def read_log_file(log_file):
    log_records = []
    
    # render "we are doomed" error styled message if log file is missing
    if not os.path.exists(log_file):
            return ["I need", "to know", "path to", "your logs darling!"]
    
    # .txt to [list] heavy lifting
    with open(log_file, 'r') as raw_log_source:
            for record in raw_log_source:
    
                    # drop '\n', blank space and  and parse record into list
                    log_records.append(record.split())
    
    # reorder log records from newest to oldest
    log_records.reverse()
    
    return log_records