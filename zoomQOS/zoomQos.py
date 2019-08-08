#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 27 18:13:13 2019

@author: nwu
"""

import requests
import copy
from secret import headers
from datetime import datetime, timedelta
from time import sleep
from math import exp


class ZoomAPIException(Exception):
    def __init__(self, response):
        self.response = response
        
    def __str__(self):
        return "{status_code: %s, reason: %s, url: %s}" % (self.response.status_code,
                                                           self.response.reason,
                                                           self.response.url)


class ZoomMultiPageTask:

    def __init__(self, url, params):
        self.url = url
        self.params = copy.deepcopy(params)
        self.accum429 = 0

    def get_all_pages(self):
        data = []
        next_page_token = ""
        params = copy.deepcopy(self.params)
        
        while True:
            if next_page_token:
                params["next_page_token"] = next_page_token
                
            response = requests.get(self.url, params=params, headers=headers)
            # we should check return code to handle errors
            # zoom API contains error code tables:
            # https://marketplace.zoom.us/docs/api-reference/error-definitions
            print(response.status_code)
            if not response.ok:
                # some error cannot continue,
                # for such errors, handle_error will raise exception
                self.handle_error(response)
                continue

            self.accum429 = 0
        
            # if code reach here, we should fetch the data we want and store them
            # also, code reach here, we should update next_page_token
            json_data = response.json()
            next_page_token = json_data["next_page_token"]

            data_for_this_loop = self.fetch_data_from_json(json_data)
            data.extend(data_for_this_loop)
            
            if self.should_stop(json_data):
                break

        return data

    def handle_error(self, response):
        if response.status_code == 429 or response.status_code == 404:
            self.accum429 += 1
            sleep(5 + exp(-self.accum429) * 10)
        else:
            raise ZoomAPIException(response)

    def should_stop(self, json_data):
        return True

    def fetch_data_from_json(self, json_data):
        return []


class FetchMeetings(ZoomMultiPageTask):

    def __init__(self, url, from_date, to_date, page_size=300, type="past"):
        self.from_date = from_date
        self.to_date = to_date
        self.page_size = page_size
        self.type = type
        params = {
            "page_size": str(page_size),
            "type": type,
            "from": from_date.strftime("%Y-%m-%d"),
            "to": to_date.strftime("%Y-%m-%d")
        }
        super().__init__(url, params)

    def should_stop(self, json_data):
        return len(json_data["next_page_token"]) == 0

    def fetch_data_from_json(self, json_data):
        return [meeting["id"]
                for meeting in json_data["meetings"]]
        

class FetchMeetingQos(ZoomMultiPageTask):
    
    def __init__(self, url, page_size=10, type="past" ):
        self.page_size = page_size
        self.type = type
        params = {
            "page_size": str(page_size),
            "type": type,
        }
        super().__init__(url, params)
        
    def should_stop(self, json_data):
        return len(json_data["next_page_token"]) == 0
    
    def fetch_data_from_json(self, json_data):
        return json_data["participants"]
        #[{},{},...]the number of dictionary is the participants amount
        

def trans_compound_data_to_str(name, compound_value):
    value_str = ",".join([("%s:%s" % (k, v)) 
                            for k, v in compound_value.items()])    
    return value_str


def handle_one_time_sample_qos(data, meeting_id, participant):
    info = [str(meeting_id), str(participant["user_name"]), data["date_time"], str(participant["location"]), str(participant["network_type"]), str(participant["data_center"]) ] 
    names = ["audio_input", "audio_output", "video_input", "video_output"]
    for name in names:
        info.append(trans_compound_data_to_str(name, data[name]))
    return "#".join(info)


def handle_one_meeting_qos(qos, meeting_id):
    lines = []
    for participant in qos:
        samples  = participant["user_qos"]
        for sample in samples:
            #line = handle_one_time_sample_qos(sample, meeting_id, participant["user_name"] )
            line = handle_one_time_sample_qos(sample, meeting_id, participant )
            lines.append(line)
    return lines
    
    
    
if __name__ == "__main__":
    
    now = datetime.now()
    fetch_meetings = FetchMeetings("https://api.zoom.us/v2/metrics/meetings",
                                   now - timedelta(18),
                                   now - timedelta(11))
    meetings = fetch_meetings.get_all_pages()
#    with open('meetings.txt', 'w') as f:
#        for id in meetings:
#           print (id, file=f)
    

    all_qos_data = []
    for idd in meetings:
        job = FetchMeetingQos("https://api.zoom.us/v2/metrics/meetings/{0}/participants/qos".format(idd))
        meeting_qos = job.get_all_pages()
        all_qos_data.append((idd,meeting_qos))
    
    all_lines = []
    with open('qos.txt_2', 'w') as f:
        for meeting_id, qos in all_qos_data:
            lines = handle_one_meeting_qos(qos, meeting_id)
            for line in lines:
                print (line, file=f)
    
    
    print (datetime.now())
    
    
    
    
    
    
    
    
    
    
    
    
    