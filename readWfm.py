from readMAT import return_type_as_string

import requests
from requests_negotiate_sspi import HttpNegotiateAuth
import json
import warnings
import numpy as np

import shutil
from loadMATLib import loadmat


print("3. Read Waveform-------------------")
wfm_mat_path = 'mat_plus_new_metadata_sample=1[]_tambient=25[C]_Vsup=13.5[V]_Iload=0.1[A]_REP=00001[].mat'
print("3.1 new mat loop")
wfm_mat = loadmat(wfm_mat_path)
dt = wfm_mat['data']


first_json_write = {}
first_json_write['deepIndexing'] = []
with open('out_json_wfm.json', 'w', encoding='utf-8') as outfile:
        json.dump(first_json_write, outfile, indent=4)

#get conditions
dt_params = dt['param']
condition_mat = []

for key_cond in dt_params.keys():
    #iterate over all conditions 
    dt_params_middle = dt_params[key_cond]
    cond_dict ={}
    cond_dict['name'] = key_cond
    cond_dict['value'] = str(dt_params_middle['value'])
    cond_dict['unit'] = dt_params_middle['unit']
    condition_mat.append(cond_dict)  

out_json = {}  
out_json['artifact_metadata'] = {}
out_json['artifact_metadata']['artifact_id'] = "This is the Nr. 1 test corner."
out_json['artifact_metadata']['username'] = "Xing Jin"
out_json['artifact_metadata']['source'] = "local test"
out_json['artifact_metadata']['filetype'] = "atv-ps-wfm"

out_json['metadata'] = {}
out_json['metadata']['timestamp'] = "dummy value"

out_json['operating_conditions'] = {}
out_json['operating_conditions'] = condition_mat


dt_out = dt['out']
#loop over all out
for key_out in dt_out.keys():
    out_json['channel'] = {}
    channel_metadata={}
    dt_out_middle = dt_out[key_out]
    # since name of the out is in the 7th row
    channel_metadata['name'] = key_out
    channel_metadata['type'] = return_type_as_string(dt_out_middle['value'])

    out_json['channel']['metadata'] = channel_metadata
    out_json['channel']['pathtype'] = "atv_ps_wfm"
    out_json['channel']['pathspec'] = "data{1, 1}.out." + str(key_out)

    with open("out_json_wfm.json", "r+") as outfile:
        data = json.load(outfile)
        #data.update(out_json)
        data['deepIndexing'].append(out_json) #first_json_write['deepIndexing'].append(out_json)
        outfile.seek(0)
        json.dump(data, outfile, indent=4)