import requests
from requests_negotiate_sspi import HttpNegotiateAuth
import json
import warnings
import numpy as np

warnings.filterwarnings('ignore')

print("1. Authorizing-------------------")
session = requests.session()
session.verify = "ca-bundle.crt"

base_url = 'https://aimlms.muc-gp.icp.infineon.com'
project_key= 'AIMLTST2'

response = session.get(f'{base_url}/v1/oauth/token', auth=HttpNegotiateAuth())
print(f'Status: {response.status_code}\nText: {response.text}')

token = json.loads(response.text)

headers = {
    'accept': 'application/json',
    'Authorization': "Bearer {}".format(token['access_token'])
}
session.headers.update(headers)
# access 

# #To test if everything is working correctly
# response = session.get(f'{base_url}/')
# print(response.status_code, ': ', response.text)
# response = session.get(f'{base_url}/health')
# print(response.status_code, ': ', response.text)

# #To get a list of all the available artifacts in your project
# response = session.get(f'{base_url}/v1/projects/{project_key}/artifacts/metadata')
# project_list = json.loads(response.text)
# print('Response Received: ' + str(response.status_code) )



print("3. Go inside-------------------")
from loadMATLib import loadmat
overall_mat_path = 'newMat.mat'
print("3.1 new mat loop")
overall_mat = loadmat(overall_mat_path)
dt = overall_mat['subsets']['data']
dim_m, dim_n = dt.shape
test_corners_start = 8

num_params = np.count_nonzero(dt[0,:] == 'param')

conditions_mat = []

for idx in range(test_corners_start,dim_m):
    condition_mat = []
    for num_param in range(num_params):
        cond_dict ={}
        cond_dict['name'] = dt[7, 1 + num_param]
        cond_dict['value'] = dt[idx, 1 + num_param]
        cond_dict['unit'] = dt[6, 1 + num_param]
        condition_mat.append(cond_dict)
        
    conditions_mat.append(condition_mat)

print(len(conditions_mat)) #out: 27 
print(conditions_mat[0]) #out: [{'name': 'tambient', 'value': -40, 'unit': 'C'}, {'name': 'Vsup', 'value': 13.5, 'unit': 'V'}, {'name': 'Iload', 'value': 0.1, 'unit': 'A'}]


print("3.2 Downlaod-------------------")
#Download an Artifact
import shutil
current_waveform = 'currentWaveform.mat'
# artifact_id = '271dd7349ed049c7b9d13e7e057f75c7'
 
# response = session.get(f'{base_url}/v1/projects/{project_key}/artifacts/{artifact_id}', stream=True)
# response.raw.decode_content = True
# with open(current_waveform, 'wb') as f:
#    shutil.copyfileobj(response.raw, f)     
# print('Response Received: ' + str(response.status_code))

# !!! nuplaod wfm files and return list of artifact ids
wfm_list=['271dd7349ed049c7b9d13e7e057f75c7', '1219d27b7ec545119142dedb42ac3c8b', '84f3ead69aad4e8c9c8f748c60d6b3ba']

# # upload an artifact 
#print("111 Downlaod-------------------")
# filename = 'outNew_12May2021141644.mat' # Path to the raw data file to be uploaded
 
# metadata = {
#     "Hi": "there!"
# }
 
# files = {
#     'metadata': (None, json.dumps(metadata), 'application/json'),
#     'rawDataFile': (filename, open(filename, 'rb'), 'text/plain')
# }
 
# response = session.post(f'{base_url}/v1/projects/{project_key}/artifacts', files=files)
 
# print('Response Received: ' + str(response.status_code) + ': ' + response.text)

# dict_out = json.loads(response.text)

# print(dict_out['artifactID'])



print("3.3 wfm matching")
# go inside the data{1,1} scope
#import scipy.io as scio
# loadmat method from scipy.io
#mat_waveform = sio.loadmat(current_waveform, struct_as_record=False)['data'][0,0][0,0]

mat_waveform = loadmat(current_waveform)

var_param = mat_waveform['data']['param']
fields = var_param.keys()
conditions_wvf = {}

for field in fields:
    conditions_wvf[field] = var_param[field]['value']

print(type(var_param))
print(conditions_wvf)
print(len(conditions_wvf))
# delete the content of the file
open(current_waveform,"w").close()

print("current written operations done!")
# deep indexing operaitons


# for each new .mat generate a josn listing all relevant files

# go inside the overall .mat file and loop through the test corners 


# go inside the current selected .mat file and check whether it matches the current condition 