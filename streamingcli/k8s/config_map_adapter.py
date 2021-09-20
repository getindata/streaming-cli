from kubernetes import config, dynamic
from kubernetes.client import api_client
from streamingcli.project.project_config import ProjectConfig
from streamingcli.k8s.project_config_map import ProjectConfigMap, ProjectConfigMapFactory
from streamingcli.Config import PROJECT_CONFIG_FILE_NAME
from kubernetes.client.exceptions import ApiException


# https://github.com/kubernetes-client/python/blob/master/examples/dynamic-client/configmap.py
class ProjectConfigMapAdapter:

    @staticmethod
    def _fetch_k8s_configmap(api, configmap_name: str):
        try:
            return api.get(
                name=configmap_name, namespace="default", label_selector="streaming=true"  # TODO set K8S namespace in project config
            )
        except ApiException as err:
            if err.status == 404:
                return None
            else:
                raise err


    @staticmethod
    def load_project_config_map(project_config: ProjectConfig):
        # Creating a dynamic client
        client = dynamic.DynamicClient(
            api_client.ApiClient(configuration=config.load_kube_config())
        )

        # fetching the configmap api
        api = client.resources.get(api_version="v1", kind="ConfigMap")

        configmap_name = project_config.project_configmap_name

        configmap_list = ProjectConfigMapAdapter._fetch_k8s_configmap(api, configmap_name)
        if configmap_list is None:
            return ProjectConfigMapFactory.create_from_project_config(project_config)
        else:
            configmap_json = configmap_list.data['project_configmap.json']
            return ProjectConfigMapFactory.create_from_json(configmap_json)

    @staticmethod
    def update_project_config_map(project_config: ProjectConfig, project_configmap: ProjectConfigMap):
        # Creating a dynamic client
        client = dynamic.DynamicClient(
            api_client.ApiClient(configuration=config.load_kube_config())
        )

        # fetching the configmap api
        api = client.resources.get(api_version="v1", kind="ConfigMap")

        configmap_name = project_config.project_configmap_name

        configmap_manifest = {
            "kind": "ConfigMap",
            "apiVersion": "v1",
            "metadata": {
                "name": configmap_name,
                "labels": {
                    "streaming": "true",
                },
            },
            "data": {
                "project_configmap.json": project_configmap.to_json(),
            },
        }

        current_configmap = ProjectConfigMapAdapter._fetch_k8s_configmap(api, configmap_name)
        if current_configmap is None:
            configmap = api.create(body=configmap_manifest, namespace="default")  # TODO set K8S namespace in project config
        else:
            configmap_patched = api.patch(
                name=configmap_name, namespace="default", body=configmap_manifest  # TODO set K8S namespace in project config
            )

    @staticmethod
    def delete(project_config: ProjectConfig):
        # Creating a dynamic client
        client = dynamic.DynamicClient(
            api_client.ApiClient(configuration=config.load_kube_config())
        )

        # fetching the configmap api
        api = client.resources.get(api_version="v1", kind="ConfigMap")

        configmap_name = project_config.project_configmap_name
        api.delete(name=configmap_name, body={}, namespace="default")

