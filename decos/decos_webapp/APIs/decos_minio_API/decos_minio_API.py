from minio import Minio
import re
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
        
    def get_sample_list(self,lab):
        data_locations = []
        pattern = r"s(\_[a-zA-Z0-9]+){2}"
        for bucket in self.client.list_buckets():
            tags = self.client.get_bucket_tags(bucket.name)
            if tags is not None:
                for tag in tags:
                    if tag == "lab":
                        if tags[tag] == lab.lab_id.lower():
                            objects = self.client.list_objects(bucket.name)
                            for obj in objects:
                                try:
                                    sample_id_s = re.search(pattern, obj.object_name)
                                    data_locations.append((sample_id_s.group() , obj))
                                except Exception as e:
                                    print(f"debug: {e}")
        return data_locations
        