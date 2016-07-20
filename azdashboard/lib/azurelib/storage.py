from googleapiclient.http import MediaFileUpload

from azdashboard.lib.azurelib.core.entity import AzEntity


__author__ = 'daniel'


class AzContainer(AzEntity):
    def __init__(self, service, container_name=""):
        super(AzContainer, self).__init__(service, container_name)

    def create(self, public=False):
        access_type = "blob" if public else None
        self._service.create_container(container_name=self._name, x_ms_blob_public_access=access_type)

    def set_container_access_type(self, container_name, public=False):
        access_type = "blob" if public else None
        self._service.set_container_acl(container_name, x_ms_blob_public_access=access_type)

    def list_containers(self):
        return [container.name for container in self._service.list_containers()]

    def exists(self):
        return self._name in self.list_containers()

    def delete_container(self, container_name):
        self._service.delete_container(container_name)

    def list_blobs(self, container_name):
        return self._service.list_blobs(container_name)


class AzBlob(AzEntity):
    def __init__(self, service, blob_name=""):
        self._container = None
        super(AzBlob, self).__init__(service, blob_name)

    def set_container(self, container):
        if type(container) is AzContainer:
            self._container = container.get_name()
        else:
            self._container = container

    def upload_file(self, file_path):
        blob_name = self._name
        blob_type = MediaFileUpload(file_path).mimetype()
        self._service.put_block_blob_from_path(self._container,
                                               blob_name,
                                               file_path,
                                               x_ms_blob_content_type=blob_type)

    def upload_io(self, content, content_type, compressed=False):
        if compressed:
            self._service.put_block_blob_from_bytes(self._container,
                                                    self._name, content,
                                                    content_encoding="gzip",
                                                    x_ms_blob_content_type=content_type)
        else:
            self._service.put_block_blob_from_bytes(self._container,
                                                    self._name, content,
                                                    x_ms_blob_content_type=content_type)

    def get_properties(self):
        return self._service.get_blob_properties(self._container, self._name)

    def delete(self):
        self._service.delete_blob(self._container, self._name)

    def download(self, destination_path):
        self._service.get_blob_to_path(self._container, self._name, destination_path)
