import requests
from requests import sessions
import re
import json
import time


# Usage: server = Server("http...host" ("id", "token"))
class Server:
    host = None
    credentials = None
    session = None

    def __init__(self, host, credentials):
        self.session = sessions.session()
        self.host = host
        self.credentials = credentials

    def get_jobs(self, *args, **kwargs):
        if args:
            subfolder = args[0]
        else:
            subfolder = kwargs.get('subfolder', None)
        job_list = []
        if subfolder:
            debug = f"{self.host}/job/{subfolder}/api/json?tree=jobs[name]"
            response = self.session.get(f"{self.host}/job/{subfolder}/api/json?tree=jobs[name]", auth=self.credentials)
        else:
            debug = f"{self.host}api/json?tree=jobs[name]"
            response = self.session.get(f"{self.host}api/json?tree=jobs[name]", auth=self.credentials)
        full_info = response.json()
        for job in full_info['jobs']:
            match = re.search(r'\.([^.\s]+)\s*$', job['_class'])
            if match:
                job_list.append({f"type": f"{match.group(1)}", "name": f"{job['name']}"})
            else:
                job_list.append({"type": f"{job['_class']}", "name": f"{job['name']}"})
        return job_list

    def get_job_folders(self, *args, **kwargs):
        if args:
            subfolder = args[0]
        else:
            subfolder = kwargs.get('subfolder', None)
        folder_list = []
        for job in (job for job in self.get_jobs(subfolder=subfolder) if job['type'] == 'Folder'):
            folder_list.append(job['name'])
        return folder_list

    def _tree_manager(self, first_arg, str_arg):
        if first_arg:
            tree = f"?tree={first_arg[0]}"
        elif str_arg.get('tree', None):
            tree = f"?tree={str_arg.get('tree', None)}"
        else:
            tree = ""
        return tree

    def get_job_info(self, job_path, *args, **kwargs):
        tree = self._tree_manager(args, kwargs)
        print(f"{self.host}job/{job_path}/api/json{tree}")
        response = self.session.get(f"{self.host}job/{job_path}/api/json{tree}", auth=self.credentials)
        return response.json()

    def get_builds(self, job_path):
        tree = "builds[*]"
        return self.get_job_info(job_path=job_path, tree=tree)['builds']

    def get_build_info(self, job_path, number):
        job_path = f"{job_path}/{number}/"
        return self.get_job_info(job_path=job_path)

    @property
    def LAST_STABLE_BUILD(self):
        return "lastStableBuild"

    @property
    def LAST_BUILD(self):
        return "lastBuild"

    @property
    def LAST_SUCCESSFUL_BUILD(self):
        return "lastSuccessfulBuild"

    @property
    def LAST_FAILED_BUILD(self):
        return "lastFailedBuild"

    @property
    def LAST_UNSTABLE_BUILD(self):
        return "lastUnstableBuild"

    @property
    def LAST_UNSUCCESSFUL_BUILD(self):
        return "lastUnsuccessfulBuild"

    @property
    def LAST_COMPLETED_BUILD(self):
        return "lastCompletedBuild"

# type of requests
 # lastBuild, lastStableBuild, lastSuccessfulBuild, lastFailedBuild, lastUnstableBuild, lastUnsuccessfulBuild, lastCompletedBuild.
    def get_latest_build(self,job_path, *args, **kwargs):
        if args:
             type_of_build = args[0]
        else:
            type_of_build = kwargs.get('type_of_build', self.LAST_BUILD)
        job_path = f"{job_path}/{type_of_build}/"
        return self.get_job_info(job_path=job_path)

    def get_console_info(self, job_path, *args, **kwargs):
        if args:
            type_of_build = args[0]
        else:
            type_of_build = kwargs.get('type_of_build', self.LAST_BUILD)
        print(self.credentials)
        response = self.session.get(f"{self.host}/job/{job_path}/lastBuild/logText/progressiveText?start=0", auth=self.credentials)
        return response.text
    
    def build_job(self, job_path, secret_token, *args, **kwargs):
        if args:
            parameters = args[0]
        else:
            parameters = kwargs.get('parameters', None)
        
        if parameters:
            pass

        if kwargs.get('data', None):
            data = kwargs.get('data')
            response = requests.post(f"{self.host}/job/{job_path}/buildWithParameters", auth=self.credentials, params={"token" : secret_token }, data=data)
        else:
            response = self.session.post(f"{self.host}/job/{job_path}/build", auth=self.credentials, params={"token" : secret_token })


