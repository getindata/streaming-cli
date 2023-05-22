import tempfile

from streamingcli.project.yaml_merger import YamlMerger

from streamingcli.profile.profile_adapter import VervericaConf, DockerConf, K8SConf, ProfileConf


class ConfigMerger:
    @staticmethod
    def merge_vvp_conf(a: VervericaConf, b: VervericaConf) -> VervericaConf:
        return VervericaConf(url=b.url if b.url else a.url, namespace=b.namespace if b.namespace else a.namespace,
                             deployment_target=b.deployment_target if b.deployment_target else a.deployment_target,
                             api_token=b.api_token if b.api_token else a.api_token)

    @staticmethod
    def merge_docker_conf(a: DockerConf, b: DockerConf) -> DockerConf:
        return DockerConf(registry_url=b.registry_url if b.registry_url else a.registry_url,
                          user=b.user if b.user else a.user, password=b.password if b.password else a.password)

    @staticmethod
    def merge_k8s_conf(a: K8SConf, b: K8SConf) -> K8SConf:
        a_spec = tempfile.NamedTemporaryFile()
        b_spec = tempfile.NamedTemporaryFile()
        with open(a_spec.name, 'w') as fh:
            fh.write(a.spec)
        with open(b_spec.name, 'w') as fh:
            fh.write(b.spec)
        merged_spec = YamlMerger.merge_two_yaml(a_spec.name, b_spec.name)
        a_spec.close()
        b_spec.close()
        return K8SConf(namespace=b.namespace if b.namespace else a.namespace, spec=merged_spec)

    @staticmethod
    def merge_profile_conf(a: ProfileConf, b: ProfileConf) -> ProfileConf:
        return ProfileConf(name=b.name, deployment_mode=b.deployment_mode if b.deployment_mode else a.deployment_mode)
