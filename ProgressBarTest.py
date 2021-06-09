# import time
# from progress.bar import IncrementalBar

# mylist = [1,2,3,4,5,6,7,8]
# mylist = ['a', 'aa', 'aaa', 'aaaa', 'b', 'bb', 'bbb', 'c', 'cc', 'ccc']

# with IncrementalBar('Countdown', max = len(mylist)) as bar:
#     for item in mylist:
#         bar.next()
#         time.sleep(0.3)

import requests
from requests_negotiate_sspi import HttpNegotiateAuth
import json
import warnings
import numpy as np
import glob, os
import shutil
warnings.filterwarnings('ignore')

from readMAT import read_general_mat
from readWfm import read_waveform_mat

from alive_progress import alive_bar
import time


rep = "REP"

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

print("3. Downloading-------------------")
# currently inside the root directory 

# create folder for the storing downlowded data 
downlaod_file_folder_name = "./download_files/"
if not os.path.exists(downlaod_file_folder_name):
    os.makedirs(downlaod_file_folder_name)

# get all to be downloaded files
gen_mat_file = {}
wfm_mat_files = {}
with open('upload_files.json', "r") as uploaded_json:
    data = json.load(uploaded_json)
    gen_mat_file = data['general_mat']
    wfm_mat_files = data['wfm_mat']

list_mat_files = []
list_mat_files = wfm_mat_files
list_mat_files.append(gen_mat_file)
# # dont need to distinguish general and wfm .mat files here 
# for mat_file in list_mat_files:
#     local_filename = mat_file['file_name']
#     artifact_id = mat_file['mat_id']
#     response = session.get(f'{base_url}/v1/projects/{project_key}/artifacts/{artifact_id}', stream=True)
#     response.raw.decode_content = True
#     with open('./download_files/' + local_filename, 'wb') as f:
#         shutil.copyfileobj(response.raw, f)
#     print('Response Received: ' + str(response.status_code))
# # until this part, all .mat has been downloaded to the /download_files folder and license was copied into it--> used for the api request 


#mylist = [1,2,3,4,5,6,7,8]

with alive_bar(len(list_mat_files)) as bar:
    for mat_file in list_mat_files:

        bar()

        local_filename = mat_file['file_name']
        artifact_id = mat_file['mat_id']
        response = session.get(f'{base_url}/v1/projects/{project_key}/artifacts/{artifact_id}', stream=True)
        response.raw.decode_content = True
        with open('./download_files/' + local_filename, 'wb') as f:
            shutil.copyfileobj(response.raw, f)
        #print('Response Received: ' + str(response.status_code))

        time.sleep(0.1)



# import time
# from tqdm import tqdm
# mylist = [1,2,3,4,5,6,7,8]
# for i in tqdm(mylist):
#     time.sleep(0.3)