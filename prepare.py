import glob, os
import numpy as np
import json
import shutil

import requests
from requests_negotiate_sspi import HttpNegotiateAuth
import warnings

warnings.filterwarnings('ignore')

from readMAT import read_general_mat
from readWfm import read_waveform_mat

class Data_Uploader:
    def __init__(self, base_url, project_key):
        self.base_url = base_url
        self.project_key = project_key
        self.session = requests.session()
        self.session.verify = "ca-bundle.crt"

    def connect_to_DL(self):
        print("1. Connecting-------------------")

        response = self.session.get(f'{self.base_url}/v1/oauth/token', auth=HttpNegotiateAuth())
        print(f'Status: {response.status_code}\nText: {response.text}')

        token = json.loads(response.text)
        headers = {
            'accept': 'application/json',
            'Authorization': "Bearer {}".format(token['access_token'])
        }
        self.session.headers.update(headers)

    def upload_files(self):
        print("2. Uploading-------------------")
        rep = "REP"
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
            response = self.session.post(f'{self.base_url}/v1/projects/{self.project_key}/artifacts', files=files)
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


class Deep_Indexing_Agent:
    def __init__(self, base_url, project_key):
        self.base_url = base_url
        self.project_key = project_key
        self.session = requests.session()
        self.session.verify = "ca-bundle.crt"

    def connect_to_DL(self):
        print("1. Connecting-------------------")

        response = self.session.get(f'{self.base_url}/v1/oauth/token', auth=HttpNegotiateAuth())
        print(f'Status: {response.status_code}\nText: {response.text}')

        token = json.loads(response.text)
        headers = {
            'accept': 'application/json',
            'Authorization': "Bearer {}".format(token['access_token'])
        }
        self.session.headers.update(headers)

    def download_files(self):
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
            response = self.session.get(f'{self.base_url}/v1/projects/{self.project_key}/artifacts/{artifact_id}', stream=True)
            response.raw.decode_content = True
            with open('./download_files/' + local_filename, 'wb') as f:
                shutil.copyfileobj(response.raw, f)
            print('Response Received: ' + str(response.status_code))
        # until this part, all .mat has been downloaded to the /download_files folder and license was copied into it--> used for the api request 

    def deep_indexing_operaiton(self):
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

    # def delete_files(self):
    #     print("5. Deleting-------------------")
    #     # list_mat_id gets from uploading procedure 
    #     for arti_id in list_mat_id:
    #         #artifact_id = '4a928ba978aa4e0787757cb6ee69dd1a'
    #         artifact_id = arti_id
    #         response = self.session.delete(f'{self.base_url}/v1/projects/{self.project_key}/artifacts/{artifact_id}')
    #         print('Response Received: ' + str(response.status_code) + ': ' + response.text)


def main():
    print("---------------------This is the start of the main funciton.------------------------")
    base_url = 'https://aimlms.muc-gp.icp.infineon.com'
    project_key = 'AIMLTST2'
    data_uploader = Data_Uploader(base_url, project_key)
    data_uploader.connect_to_DL()
    data_uploader.upload_files()

    deep_Indexing_Agent = Deep_Indexing_Agent(base_url, project_key)
    deep_Indexing_Agent.connect_to_DL()
    deep_Indexing_Agent.download_files()
    deep_Indexing_Agent.deep_indexing_operaiton()
    
    print("---------------------This is the end of the main funciton.------------------------")

if __name__ == "__main__":
    main()