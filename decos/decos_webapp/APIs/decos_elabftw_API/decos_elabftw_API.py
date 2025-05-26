# This is the main library, take note that I use only requests and json
# These two libraries are the basic foundations of an API REST Interface

import requests
import json

# This is the main class
class ElabFTWAPI:
  # We override the constructor with the url of our site and our token
  def __init__(self, base_url, api_key):
    """
    Initializes the ElabFTW API client.

    Args:
        base_url: The base URL of the ElabFTW instance.
        api_key: Your API key for authentication.
    """
    self.base_url = base_url
    # Here we set the base headers to our HTTP/REST requests
    self.headers = {
        'Authorization': f'{api_key}',
        'Content-Type': 'application/json'
    }

  # This is the first request, to retrieve all the experiments,
  # please note "**kwargs", this is a way to give some search keys
  # to our requests
  def get_experiments(self, **kwargs):
    """
    Retrieves a list of experiments from ElabFTW.

    Args:
    **kwargs:  Optional parameters for filtering the experiments. Refer to the ElabFTW API docs for available filters.
              Examples:
              limit=10: Return only 10 experiments.
              page=2: Return the second page of experiments.
              title: Search for experiments with a specific title.

    Returns:
    A list of experiments in JSON format.

    "https://elab.local:3148/api/v2/experiments?q=&extended=&related=&related_origin=&cat=&tags[]=&limit=&offset=&owner=&scope=&order=&sort="

    """
    # this is the location of all our (accessible) experiments
    url = f'{self.base_url}/api/v2/experiments'
    # Here we use a GET request, because we retrieve data (beware )
    response = requests.get(url, headers=self.headers, params=kwargs)
    self._check_response(response)
    return response.json()

  # Here we ask only for a specific experiment
  def get_experiment(self, experiment_id):
    """
    Retrieves details for a specific experiment.

    Args:
    experiment_id: The ID of the experiment to retrieve.

    Returns:
    The experiment details in JSON format.
    """
    # Note the url "dynamic" node
    url = f'{self.base_url}/api/v2/experiments/{experiment_id}'
    response = requests.get(url, headers=self.headers)
    self._check_response(response)
    return response.json()

  # Here we use patch request to update our experiment
  def modify_experiment(self, experiment_id, data):
    """
    Modifies an existing experiment.

    Args:
    experiment_id: The ID of the experiment to modify.
    data: A dictionary containing the updated experiment data.

    Returns:
    The modified experiment details in JSON format.
    """
    response = requests.patch(f"{self.base_url}/api/v2/experiments/{experiment_id}", json.dumps(data), headers=self.headers)
    self._check_response(response)
    return response.json()

  # Here we use patch but first we request all the data, so we can stitch
  # together the information
  def add_to_body_of_experiment(self, experiment_id, add_to_body):
    """
    Adds text to the body of an existing experiment.

    Args:
    experiment_id: The ID of the experiment to modify.
    add_to_body: The text to add to the body.
    """
    # We get the experiment body
    old_body = self.get_experiment(experiment_id=experiment_id)['body']
    # and then we add the new part
    data = {
        "body": old_body + add_to_body
    }
    response = requests.patch(f"{self.base_url}/api/v2/experiments/{experiment_id}", json.dumps(data), headers=self.headers)
    self._check_response(response)
    return response.json()

  # Here we create a new experiment. Note that as API specifications we need to
  # first do a post request to make the empty experiment, have an ID assigned, and
  # then patch the data in.
  def create_experiment(self, data):
    """
    Creates a new experiment.

    Args:
      data: A dictionary containing the experiment data.  Structure should match ElabFTW API documentation.


    Returns:
        The newly created experiment data in JSON format.
    """
    url = f'{self.base_url}/api/v2/experiments'
    response = requests.post(url, headers=self.headers)
    self._check_response(response)
    response_list = self.get_experiments(limit=1)
    response = requests.patch(f"{self.base_url}/api/v2/experiments/{response_list[0]['id']}", json.dumps(data), headers=self.headers)
    self._check_response(response)
    return response.json()

  # This is a private method where we check the response, if it is ok (2xx)
  # we proceed, if not, we throw an exception
  def _check_response(self, response):
    """
    Checks the HTTP response for errors.

    Args:
      response: The HTTP response object.

    Raises:
      Exception: If the response indicates an error.
    """
    if not 200 <= response.status_code < 300 :
      try:
          error_data = response.json()
          error_message = error_data.get('message', 'Unknown error')
      except json.JSONDecodeError:
          error_message = response.text
      raise Exception(f'ElabFTW API request failed with status code {response.status_code}: {error_message}')

  # Here we upload a file on our experiment
  def upload_file_to_experiment(self, experiment_id, file_path, comment):
    """
    Uploads a file to a specific experiment.

    Args:
      experiment_id: The ID of the experiment.
      file_path: The local path to the file to upload.
    """
    # This is the node reserved to POST uploads
    # /{entity_type}/{id}/uploads
    url = f'{self.base_url}/api/v2/experiments/{experiment_id}/uploads'
    try:
      with open(file_path, 'rb') as file:
          files = {'file': file}
          # We put a comment to our file, this comment will be displayed on the experiment
          comment = {'comment' : comment}
          # The headers and data is a bit different here!
          response = requests.post(url, headers={'Authorization': self.headers['Authorization']}, files=files, data=comment)
          self._check_response(response)  # Check for errors
          print(f"File uploaded successfully: {response.status_code}")
    except FileNotFoundError:
      print(f"Error: File not found at {file_path}")

  # Here we add an image to the body, to do so we need first to upload the image, and
  # then write the hmtl code with the source of that image, calling the php page: download
  # passing a parameter that is the "long name" of our upload
  def add_image_to_experiment(self, experiment_id, image_path, width, height, comment):
    self.upload_file_to_experiment(experiment_id, image_path, comment)
    response = self.get_experiment(experiment_id)
    image_url = f'{response["uploads"][0]["long_name"]}'
    url_str = (
        r'<img src=' +
        r'app/download.php?f=' + image_url +
        r' width=' + str(width) + ' height=' + str(height) +
        r' alt=' + comment + '>')
    response = self.add_to_body_of_experiment(experiment_id=experiment_id, add_to_body=url_str)
    return response


