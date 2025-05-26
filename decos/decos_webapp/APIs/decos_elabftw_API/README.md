# ElabFTW API Python Library
version: 0.1 - (generated with chat-gtp, note by @marco.prenassi)
author: marco prenassi
e-mail: marco. prenassi {}areasciencepark.it, m.prenassi {}gmail.com

This document describes the structure and usage of the `ElabFTWAPI` Python library, which interacts with the ElabFTW API using HTTP requests. The library enables users to manage and retrieve data from their ElabFTW instances efficiently.

## Requirements

This library depends on the following Python packages:

- `requests`
- `json`

Ensure these dependencies are installed before using the library.

```bash
pip install requests
```

## Class: `ElabFTWAPI`

The `ElabFTWAPI` class serves as the main interface for interacting with the ElabFTW API. It requires a base URL and an API key for authentication.

### Constructor: `__init__`

```python
ElabFTWAPI(base_url, api_key)
```

#### Parameters
- `base_url` (str): The base URL of the ElabFTW instance (e.g., `https://your-elabftw-instance.com/api`).
- `api_key` (str): The API key for authenticating requests.

#### Example
```python
api = ElabFTWAPI(base_url="https://your-elabftw-instance.com/api", api_key="your_api_key")
```

---

## Methods

### `get_experiments(**kwargs)`

Retrieves a list of experiments from the ElabFTW instance.

#### Parameters
- `kwargs` (optional): Query parameters for filtering experiments.

#### Returns
- `list`: A list of experiment objects.

#### Example
```python
experiments = api.get_experiments(status="ongoing")
print(experiments)
```

### `create_experiment(data)`

Creates a new experiment.

#### Parameters
- `data` (dict): The data for the new experiment, including fields like `title` and `description`.

#### Returns
- `dict`: The created experiment's details.

#### Example
```python
experiment_data = {
    "title": "New Experiment",
    "description": "Details about the experiment."
}
response = api.create_experiment(data=experiment_data)
print(response)
```

### `update_experiment(experiment_id, data)`

Updates an existing experiment.

#### Parameters
- `experiment_id` (int): The ID of the experiment to update.
- `data` (dict): The updated data for the experiment.

#### Returns
- `dict`: The updated experiment's details.

#### Example
```python
update_data = {
    "title": "Updated Experiment Title"
}
response = api.update_experiment(experiment_id=123, data=update_data)
print(response)
```

### `delete_experiment(experiment_id)`

Deletes an experiment.

#### Parameters
- `experiment_id` (int): The ID of the experiment to delete.

#### Returns
- `dict`: A response indicating the success of the deletion.

#### Example
```python
response = api.delete_experiment(experiment_id=123)
print(response)
```

### `get_experiment(experiment_id)`

Retrieves details of a specific experiment.

#### Parameters
- `experiment_id` (int): The ID of the experiment to retrieve.

#### Returns
- `dict`: The details of the experiment.

#### Example
```python
experiment = api.get_experiment(experiment_id=123)
print(experiment)
```

---

## Error Handling

The library raises exceptions for HTTP errors. Ensure proper error handling in your code:

```python
try:
    experiments = api.get_experiments()
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
```

## Extensibility

You can extend the `ElabFTWAPI` class to add more methods for interacting with other endpoints of the ElabFTW API.

---

## Example Usage

```python
from elabftw_api import ElabFTWAPI

# Initialize the API client
api = ElabFTWAPI(base_url="https://your-elabftw-instance.com/api", api_key="your_api_key")

# Retrieve all experiments
experiments = api.get_experiments()
print(experiments)

# Create a new experiment
new_experiment = {
    "title": "My First Experiment",
    "description": "This is a test experiment."
}
response = api.create_experiment(data=new_experiment)
print(response)

# Update an experiment
update_data = {
    "title": "Updated Title"
}
response = api.update_experiment(experiment_id=123, data=update_data)
print(response)

# Delete an experiment
response = api.delete_experiment(experiment_id=123)
print(response)
```

---

## Notes

- Ensure that your API key has the necessary permissions to perform the desired actions.
- Refer to the official ElabFTW API documentation for additional details about available endpoints and parameters.

---

## License

This library is distributed under the MIT License. See `LICENSE` for more details.

