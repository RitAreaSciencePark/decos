from APIs.decos_elabftw_API.decos_elabftw_API import ElabFTWAPI
from django.template.loader import render_to_string
from PRP_CDM_app.models import LageSamples
from django.forms.models import model_to_dict
from APIs.decos_jenkins_API.decos_jenkins_API import Server
from .secrets_models import API_Tokens
import re
from django.contrib.auth.models import User, Group

# Custom exception to handle errors related to Jenkins configuration
class JenkinsConfigurationError(Exception):
    pass

# Helper class to resolve the path of a specific pipeline within Jenkins
class JenkinsPipelinePathResolver:
    def __init__(self, jenkins_client):
        # Store the Jenkins client instance
        self.jenkins_client = jenkins_client

    def resolve_pipeline_path(self, pipeline_name):
        # Iterate over all folders in Jenkins
        for folder in self.jenkins_client.get_job_folders():
            # Iterate over all jobs in the folder
            for job in self.jenkins_client.get_jobs(folder):
                # Check if the job name matches the pipeline name
                if job["name"] == pipeline_name:
                    # Return the constructed Jenkins job path
                    return f"{folder}/job/{pipeline_name}"
        # Raise an error if the pipeline is not found
        raise JenkinsConfigurationError(f"Pipeline '{pipeline_name}' not found.")

# Main Jenkins API interaction class for starting pipelines and fetching output
class DecosJenkinsAPI:
    def __init__(self, username, lab, host=None):
        # Store user and lab context
        self.username = username
        self.lab = lab
        # Default host for Jenkins if not provided
        self.host = host or 'http://jenkins-test:8080/'
        # Initialize the Jenkins client with user credentials
        self._init_client()
        # Initialize a path resolver to fetch pipeline paths later
        self.path_resolver = JenkinsPipelinePathResolver(self.client)

    def _init_client(self):
        # Retrieve user object by username
        user = User.objects.get(username=self.username)
        # Fetch the user's Jenkins token associated with the selected lab
        jenkins_token = API_Tokens.objects.filter(user_id=user, laboratory=self.lab).values("jenkins_token").first()
        if not jenkins_token:
            # Raise an error if the token is not found
            raise JenkinsConfigurationError("Jenkins token not found for user and lab.")

        # Set credentials tuple for Jenkins API authentication
        credentials = (self.username, jenkins_token['jenkins_token'])
        # Initialize Jenkins server client with credentials
        self.client = Server(self.host, credentials)

    def start_pipeline(self, pipeline_name, secret_token, data=None):
        # Resolve the Jenkins pipeline path using the resolver
        path = self.path_resolver.resolve_pipeline_path(pipeline_name)
        # Trigger the pipeline execution with the provided data and secret token
        self.client.build_job(job_path=path, secret_token=secret_token, data=data or {})

    def get_pipeline_output(self, pipeline_name):
        # Resolve the Jenkins pipeline path using the resolver
        path = self.path_resolver.resolve_pipeline_path(pipeline_name)
        # Fetch and return the console output of the pipeline
        return self.client.get_console_info(path)
