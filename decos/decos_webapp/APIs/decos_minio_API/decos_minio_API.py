from minio import Minio
from minio.error import S3Error
import re
import json
import importlib

from PRP_CDM_app.models.common_data_model import Samples
from PRP_CDM_app.models.laboratory_models.bio_open_lab_unisalento import Bio_Open_Lab_UnisalentoMetadata
class decos_minio:
    client = None   

    def __init__(self, endpoint, access_key, secret_key):
        self.client = Minio(endpoint=endpoint, access_key=access_key,
        secret_key=secret_key)

    def check(self):
        try:
            if self.client.list_buckets() is not None:
                return True
            else:
                return False
        except Exception as e:
            print(f"debug: {e}")
            return False
        
    def get_sample_list(self,lab_id):
        data_locations = []
        pattern = r"s(\_[a-zA-Z0-9]+){2}"
        lab_id = lab_id
        for bucket in self.client.list_buckets():
            tags = self.client.get_bucket_tags(bucket.name)
            if tags is not None:
                for tag in tags:
                    if tag == "lab":
                        if tags[tag].lower() == lab_id.lower():
                            objects = self.client.list_objects(bucket.name)
                            for obj in objects:
                                try:
                                    sample_id_s = re.search(pattern, obj.object_name)
                                    data_locations.append((sample_id_s.group() , obj))
                                    if obj.object_name.endswith('/'):
                                        metadata_path = obj.object_name + 'metadata.json'
                                        try:
                                            self.client.stat_object(bucket.name, metadata_path)
                                            response = self.client.get_object(bucket.name, metadata_path)
                                            metadata_bytes = response.read()
                                            metadata_obj = json.loads(metadata_bytes.decode('utf-8'))
                                            self._store_metadata_obj(metadata_obj, lab_id, sample_id_s)
                                            response.close()
                                            response.release_conn()
                                        except S3Error as e:
                                            if e.code == "NoSuchKey":
                                                continue
                                            else:
                                                raise Exception
                                except Exception as e:
                                    print(f"debug: {e}")
        return data_locations

    def _store_metadata_obj(self, metadata_obj, lab_id, sample_id_s):
        try:
            parts = sample_id_s.group().split("_")
            base_sample_id = "_".join(parts[:3])
            sample = Samples.objects.get(sample_id=base_sample_id)

            module_path = f"PRP_CDM_app.models.laboratory_models.{lab_id.lower()}"
            module = importlib.import_module(module_path)
            class_name = lab_id + "Metadata"
            model_class = getattr(module, class_name)

            metadata_id = metadata_obj.get("metadata_id")
            metadata_fields = metadata_obj.get("metadata", {})

            if metadata_id:
                try:
                    existing_metadata = model_class.objects.get(metadata_id=metadata_id)
                except model_class.DoesNotExist:
                    existing_metadata = None
            else:
                existing_metadata = None

            if existing_metadata:
                for key, value in metadata_fields.items():
                    setattr(existing_metadata, key, value)
                existing_metadata.sample = sample
                existing_metadata.save()
            else:
                metadata_fields["metadata_id"] = metadata_id
                model_class.from_minio_metadata(metadata_fields, sample)

        except (ModuleNotFoundError, AttributeError) as e:
            print(f"Error loading model for lab_id '{lab_id}': {e}")
        except Samples.DoesNotExist:
            print(f"Sample with ID '{base_sample_id}' not found.")