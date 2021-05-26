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

print("2. Uploading-------------------")
# license needs to be copied into the data storage folder since .post needs the check of the license and at the same time uploading procedure happens in the data folder
shutil.copy('ca-bundle.crt', './testDataFolder')

# get all files with .mat suffix isnide the given data storage folder 
os.chdir("./testDataFolder")
list_file = [] 
for file in glob.glob("*.mat"):
    list_file.append(file)

# needed for json log file 
list_mat_id = []
list_mat_name = []
list_mat_lastUpdated = []
for mat_file in list_file:
    #filename = 'outNew_12May2021141644.mat' # Path to the raw data file to be uploaded
    filename = mat_file # Path to the raw data file to be uploaded
    metadata = { }
    files = {
        'metadata': (None, json.dumps(metadata), 'application/json'),
        'rawDataFile': (filename, open(filename, 'rb'), 'text/plain')
    }
    response = session.post(f'{base_url}/v1/projects/{project_key}/artifacts', files=files)
    #print('Response Received: ' + str(response.status_code) + ': ' + response.text)
    dict_out = json.loads(response.text) # dict_out['artifactID'] out: 8d066226050448789f87a5c548d677e5 # dict_out['rawDataFile']['fileName'] out: outNew_12May2021141644.mat
    list_mat_id.append(dict_out['artifactID'])
    list_mat_name.append(dict_out['rawDataFile']['fileName'])
    list_mat_lastUpdated.append(dict_out['lastUpdated'])
print(len(list_mat_id))
os.chdir("..")

# write id, name and last modified date to the log json file  
json_upload = {}
json_upload_wfm = []
for i in range(len(list_mat_name)):
    tmp_mat= {}
    # check whether current file is the general .mat file or waveform 
    if rep not in list_mat_name[i]:
        tmp_mat['mat_id'] =list_mat_id[i]
        tmp_mat['file_name'] = list_mat_name[i]
        tmp_mat['lastUpdated'] = list_mat_lastUpdated[i]
        json_upload['general_mat'] = tmp_mat
    else:
        tmp_mat['mat_id'] =list_mat_id[i]
        tmp_mat['file_name'] = list_mat_name[i]
        tmp_mat['lastUpdated'] = list_mat_lastUpdated[i]
        json_upload_wfm.append(tmp_mat)
json_upload['wfm_mat'] = json_upload_wfm

output_file_path = './upload_files.json'
with open(output_file_path, 'w', encoding='utf-8') as outfile:
        json.dump(json_upload, outfile, indent=4)
# until this part, all .mat has been uploaded to DL and a json file is generated 


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
# dont need to distinguish general and wfm .mat files here 
for mat_file in list_mat_files:
    local_filename = mat_file['file_name']
    artifact_id = mat_file['mat_id']
    response = session.get(f'{base_url}/v1/projects/{project_key}/artifacts/{artifact_id}', stream=True)
    response.raw.decode_content = True
    with open('./download_files/' + local_filename, 'wb') as f:
        shutil.copyfileobj(response.raw, f)
    print('Response Received: ' + str(response.status_code))
# until this part, all .mat has been downloaded to the /download_files folder and license was copied into it--> used for the api request 

print("4. Read Files -------------------")
# currently inside the root directory 

# create output json folder 
output_folder_name = "./output_json/"
if not os.path.exists(output_folder_name):
    os.makedirs(output_folder_name)

# get all downloaded and to be analyzed files
with open('upload_files.json', "r") as uploaded_json:
    data = json.load(uploaded_json)
    gen_mat_file = data['general_mat']
    wfm_mat_files = data['wfm_mat']

# create json for general .mat file 
read_general_mat(gen_mat_file)
# create json for waveform .mat files 
for i in range(len(wfm_mat_files)):
    read_waveform_mat(wfm_mat_files[i])
os.chdir("..")

print("5. Deleting-------------------")
# list_mat_id gets from uploading procedure 
for arti_id in list_mat_id:
    #artifact_id = '4a928ba978aa4e0787757cb6ee69dd1a'
    artifact_id = arti_id
    response = session.delete(f'{base_url}/v1/projects/{project_key}/artifacts/{artifact_id}')
    print('Response Received: ' + str(response.status_code) + ': ' + response.text)