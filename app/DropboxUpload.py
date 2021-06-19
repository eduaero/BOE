import dropbox
import os
import pandas as pd
import datetime
import numpy as np

class DropboxBoe:
    def __init__(self, dropbox_key, identifier, upload_every_x_min = 60):
        self.dropbox_key = dropbox_key
        self.clientDropbox = dropbox.Dropbox(self.dropbox_key)
        self.identifier = identifier

        self.file_json = "subastas_" + identifier + ".json"
        self.json_local_file_date = None

        self.json_dropbox_file_date = None
        self.json_dropbox_path = '/' + identifier + '/' + self.file_json

        self.json_action_download = False
        self.json_upload_last_date = None
        self.json_upload_last_count = 0

        self.upload_every_x_min = upload_every_x_min

    def re_do_login(self):
        self.clientDropbox = dropbox.Dropbox(self.dropbox_key)

    def account_information(self):
        self.account_information = self.clientDropbox.users_get_current_account()
        print(self.account_information)
        # print(account_information["email"])
        # print(account_information["name"]["display_name"])
        # print("Signed in with account: %s and email: %s" %(account_information["name"]["display_name"] ,account_information["email"]) )

    def check_files_dropbox(self):
        # 3. Get the list of files in the current Dropbox repository
        response = self.clientDropbox.files_list_folder(path="/" + self.identifier)
        list_files = response.entries
        len_files = len(list_files)
        print("Number of files: %d" % len_files)

        all_files = pd.DataFrame({"File_name": [], "Date": []})
        for files in list_files:
            if 'client_modified' in files._all_field_names_:
                all_files = all_files.append(pd.DataFrame({"File_name": [files.name], "Date": [files.client_modified]}))

        check_files = sum(self.file_json == all_files.File_name) # String used for the check
        if check_files == 1:
            # self.json_dropbox_file = True
            self.json_dropbox_file_date = all_files.Date[all_files.File_name == self.file_json].values[0]
        elif check_files > 1:
            print("It might be an error, more than one file with the same name found in Dropbox")
        # else:
            # self.json_dropbox_file = False

    def check_files_local(self):
        # 4. Get the files in the current folder
        files_local_machine = os.listdir()
        file_json_exists = self.file_json in files_local_machine
        if file_json_exists:
            modTimesinceEpoc = os.path.getmtime(self.file_json)
            self.json_local_file_date = np.datetime64(datetime.datetime.fromtimestamp(modTimesinceEpoc))
    def update_files(self):
        # 3. Get the list of files in the current Dropbox repository
        self.check_files_dropbox()
        # 4. Get the files in the current folder
        self.check_files_local()

        # Logic for deciding when to download the file from Dropbox
        if self.json_local_file_date is None and self.json_dropbox_file_date is None:
            self.json_action_download = False
        elif self.json_dropbox_file_date is None:
            self.json_action_download = False
        elif self.json_local_file_date is None and self.json_dropbox_file_date is not None:
            self.json_action_download = True
        elif self.json_dropbox_file_date > self.json_local_file_date:
            self.json_action_download = True

        if self.json_action_download:
            self.download_file_Dropbox()

    def download_file_Dropbox(self):
        # Download the file from Dropbox
        if self.json_action_download:
            self.clientDropbox.files_download(self.json_dropbox_path)
            self.print_download_file_dropbox()

    def upload_file_Dropbox(self):
        file = open(self.file_json, 'rb')
        self.clientDropbox.files_alpha_upload(file.read(), self.json_dropbox_path,
                                                    mode=dropbox.files.WriteMode.overwrite)
        self.print_upload_file_dropbox()
        # It should be introduced if succesfully uplaoded only
        # It should be introduced if succesfully uplaoded only
        # It should be introduced if succesfully uplaoded only
        self.json_upload_last_date = np.datetime64(datetime.datetime.now())
        self.json_upload_last_count = self.json_upload_last_count + 1

    def upload_every_x_mins(self):
        print(" - - - E N T E R S - U P L O A D - E V E R Y - X - M I N S - - - ")
        if self.json_upload_last_date is None:
            self.upload_file_Dropbox()
            time_dif_mins = 0
        else:
            time_dif = np.datetime64(datetime.datetime.now()) - self.json_upload_last_date
            time_dif_mins = time_dif.astype('timedelta64[m]')  / np.timedelta64(1, 'm')
            # print("Time diff is %f mins" % time_dif_mins)

        if time_dif_mins > self.upload_every_x_min:
            self.upload_file_Dropbox()

    def print_upload_file_dropbox(self):
        print("- - - - - - - - - - - - - - - - - - - - - - - - ")
        print("F I L E _ U P L O A D E D _ T O _ D R O P B O X ")
        print("- - - - - - - - - - - - - - - - - - - - - - - - ")
    def print_download_file_dropbox(self):
        print("- - - - - - - - - - - - - - - - - - - - - - - - - - - ")
        print("F I L E _ D O W N L O A D E D _ T O _ D R O P B O X ")
        print("- - - - - - - - - - - - - - - - - - - - - - - - - - - ")


# # Parameters defined
# upload_every_x_min = 1
# identifier = "boe"
# dropbox_key = 'M_PyPzZUBqkAAAAAAAAAAb17i6RAGPpoCMW83T75c4PcS3BEIgFZKD8N0NoN8_82'
#
#  # 1. Initialize the object
# DropboxBoe = DropboxBoe(dropbox_key, identifier, upload_every_x_min)
# # 2. Upload the required files
# DropboxBoe.update_files()
# # 3. Upload the file
# DropboxBoe.upload_every_x_mins()







