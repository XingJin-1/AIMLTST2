import requests
from requests_negotiate_sspi import HttpNegotiateAuth
import json
import warnings
import numpy as np

import shutil


def return_type_as_string(in_var):
    if type(in_var) == float:
        return "double"
    elif type(in_var) == str:
        return "string"
    elif type(in_var) == int:
        return "integer"

print("3. Read General .MAT File--------------------")
from loadMATLib import loadmat
overall_mat_path = 'newMat.mat'
print("3.1 new mat loop")
overall_mat = loadmat(overall_mat_path)
dt = overall_mat['subsets']['data']
dim_m, dim_n = dt.shape
test_corners_start = 8
   
num_params = np.count_nonzero(dt[0,:] == 'param')

index_out = np.where(dt[0,:] == 'out')
index_aux = np.where(dt[0,:] == 'aux')

conditions_mat = []

first_json_write = {}
first_json_write['deepIndexing'] = []

with open('out_json_new.json', 'w', encoding='utf-8') as outfile:
        json.dump(first_json_write, outfile, indent=4)


for idx in range(test_corners_start, dim_m): # number of test corners
    # construct condition block 
    condition_mat = []
    for num_param in range(num_params): # number of params 
        cond_dict ={}
        cond_dict['name'] = dt[7, 1 + num_param]
        cond_dict['value'] = str(dt[idx, 1 + num_param])
        cond_dict['unit'] = dt[6, 1 + num_param]
        condition_mat.append(cond_dict)  
    conditions_mat.append(condition_mat)
    # print(conditions_mat[5]) #out: [{'name': 'tambient', 'value': -40, 'unit': 'C'}, {'name': 'Vsup', 'value': 13.5, 'unit': 'V'}, {'name': 'Iload', 'value': 0.1, 'unit': 'A'}]  
    
    # construct channel block 
    # out:{'channel': {'metadata': {'name': 'Reg2', 'type': 'integer'}}, 'pathtype': 'atv_ps_mat', 'pathspec': 'subsets.data{9,6}'}
    

    out_json = {}  
    out_json['artifact_metadata'] = {}
    out_json['artifact_metadata']['artifact_id'] = "This is the Nr." + str(idx-7) + " test corner."
    out_json['artifact_metadata']['username'] = "Xing Jin"
    out_json['artifact_metadata']['source'] = "local test"
    out_json['artifact_metadata']['filetype'] = "atv-ps-mat"

    out_json['metadata'] = {}
    out_json['metadata']['timestamp'] = "dummy value"

    out_json['operating_conditions'] = {}
    out_json['operating_conditions'] = condition_mat

    #loop over all out
    for idx_out in index_out[0]:
        out_json['channel'] = {}
        channel_metadata={}
        # since name of the out is in the 7th row
        channel_metadata['name'] = dt[7, idx_out]
        channel_metadata['type'] = return_type_as_string(dt[idx, idx_out])

        out_json['channel']['metadata'] = channel_metadata
        out_json['channel']['pathtype'] = "atv_ps_mat"
        out_json['channel']['pathspec'] = "subsets.data{" + str(idx+1) + "," + str(idx_out+1) + "}"

        with open("out_json_new.json", "r+") as outfile:
            data = json.load(outfile)
            #data.update(out_json)
            data['deepIndexing'].append(out_json) #first_json_write['deepIndexing'].append(out_json)
            outfile.seek(0)
            json.dump(data, outfile, indent=4)

    #loop over all aux
    for idx_aux in index_aux[0]:
        out_json['channel'] = {}
        channel_metadata={}
        # since name of the out is in the 7th row
        channel_metadata['name'] = dt[7, idx_aux]
        channel_metadata['type'] = return_type_as_string(dt[idx, idx_aux])

        out_json['channel']['metadata'] = channel_metadata
        out_json['channel']['pathtype'] = "atv_ps_mat"
        out_json['channel']['pathspec'] = "subsets.data{" + str(idx+1) + "," + str(idx_aux+1) + "}"

        with open("out_json_new.json", "r+") as outfile:
            data = json.load(outfile)
            #data.update(out_json)
            data['deepIndexing'].append(out_json) #first_json_write['deepIndexing'].append(out_json)
            outfile.seek(0)
            json.dump(data, outfile, indent=4)



# print(len(conditions_mat)) #out: 27 
# print(conditions_mat[5]) #out: [{'name': 'tambient', 'value': -40, 'unit': 'C'}, {'name': 'Vsup', 'value': 13.5, 'unit': 'V'}, {'name': 'Iload', 'value': 0.1, 'unit': 'A'}]

# out_json = {}
# out_json["operating_conditions"] = []
# for i in range(len(conditions_mat)):
#     out_json["operating_conditions"].append(conditions_mat[i])

# with open('out_json.txt', 'w', encoding='utf-8') as outfile:
#     json.dump(out_json, outfile, indent=4)

# print(json.dumps(conditions_mat[5], indent=4))
# print(dt[0,:])
# print(dt[0,:][0])