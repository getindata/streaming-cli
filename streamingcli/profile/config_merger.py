from typing import Optional

from streamingcli.project.yaml_merger import YamlMerger

from streamingcli.profile.profile_adapter import VervericaConf, K8SConf, ScliProfile


class ConfigMerger:
    @staticmethod
    def merge_vvp_conf(a: VervericaConf, b: VervericaConf) -> Optional[VervericaConf]:
        if a is None or b is None:
            return a or b
        return VervericaConf(url=b.url if b.url else a.url, namespace=b.namespace if b.namespace else a.namespace,
                             deployment_target=b.deployment_target if b.deployment_target else a.deployment_target,
                             api_token=b.api_token if b.api_token else a.api_token)

    @staticmethod
    def merge_k8s_conf(a: K8SConf, b: K8SConf) -> Optional[K8SConf]:
        if a is None or b is None:
            return a or b

        return K8SConf(namespace=b.namespace if b.namespace else a.namespace,
                       spec=YamlMerger.merge_two_yaml_str(a.spec, b.spec))

    @staticmethod
    def merge_profiles(base: ScliProfile, extra: ScliProfile) -> ScliProfile:
        return ScliProfile(profile_name=extra.profile_name,
                           deployment_mode=extra.deployment_mode or base.deployment_mode,
                           docker_registry_url=extra.docker_registry_url or base.docker_registry_url,
                           ververica_conf=ConfigMerger.merge_vvp_conf(base.ververica_conf, extra.ververica_conf),
                           flink_conf=YamlMerger.merge_two_yaml_str(base.flink_conf, extra.flink_conf),
                           k8s_conf=ConfigMerger.merge_k8s_conf(base.k8s_conf, extra.k8s_conf),
                           resources_conf=YamlMerger.merge_two_yaml_str(base.resources_conf, extra.resources_conf))
