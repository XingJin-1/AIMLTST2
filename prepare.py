import requests
from requests_negotiate_sspi import HttpNegotiateAuth
import json
import warnings
import numpy as np
import glob, os
warnings.filterwarnings('ignore')

from readMAT import read_general_mat
from readWfm import read_waveform_mat

# print("1. Authorizing-------------------")
# session = requests.session()
# session.verify = "ca-bundle.crt"

# base_url = 'https://aimlms.muc-gp.icp.infineon.com'
# project_key= 'AIMLTST2'

# response = session.get(f'{base_url}/v1/oauth/token', auth=HttpNegotiateAuth())
# print(f'Status: {response.status_code}\nText: {response.text}')

# token = json.loads(response.text)

# headers = {
#     'accept': 'application/json',
#     'Authorization': "Bearer {}".format(token['access_token'])
# }
# session.headers.update(headers)

# print("2. Uploading-------------------")
# filename = 'outNew_12May2021141644.mat' # Path to the raw data file to be uploaded
# metadata = {
# }
# files = {
#     'metadata': (None, json.dumps(metadata), 'application/json'),
#     'rawDataFile': (filename, open(filename, 'rb'), 'text/plain')
# }
 
# response = session.post(f'{base_url}/v1/projects/{project_key}/artifacts', files=files)
 
# print('Response Received: ' + str(response.status_code) + ': ' + response.text)
# dict_out = json.loads(response.text)
# print(dict_out['artifactID'])

print("3. Read Files --------------------------")
os.chdir("./testDataFolder")
list_file = [] 
for file in glob.glob("*.mat"):
    list_file.append(file)

rep = "REP"
list_wfm = []
[list_wfm.append(list_file[i]) for i in range(len(list_file)) if rep in list_file[i]]
list_general_mat = []
[list_general_mat.append(list_file[i]) for i in range(len(list_file)) if rep not in list_file[i]]

os.chdir("..")
output_folder_name = "./output_json/"
if not os.path.exists(output_folder_name):
    os.makedirs(output_folder_name)

read_general_mat(list_general_mat[0])

for i in range(len(list_wfm)):
    read_waveform_mat(list_wfm[i])

os.chdir("..")


# from loadMATLib import loadmat
# from pathlib import Path

# overall_mat = loadmat('./testDataFolder/mat_plus_new_metadata_sample=1[].mat')

# dt = overall_mat['subsets']['data']
# print(dt)