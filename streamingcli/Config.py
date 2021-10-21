from pathlib import Path

INITIAL_PROJECT_REPO = "git@gitlab.com:getindata/streaming-labs/flink-sandbox-python.git"
PROJECT_LOCAL_CONFIG_FILE_NAME = ".streaming_config.yml"
PROJECT_LOCAL_TEMPLATE_DIR_NAME = ".vvp"
PROJECT_K8S_CONFIGMAP_KEY = "project_configmap.json"
PLATFORM_K8S_CONFIGMAP_NAME = "streaming-platform-config"
PLATFORM_K8S_CONFIGMAP_KEY = "platform_config.json"
PLATFORM_K8S_SECRET_NAME = "streaming-platform-secret"
PLATFORM_DEFAULT_DEPLOYMENT_TARGET_NAME = "default"
PROFILE_ENV_VARIABLE_NAME = "SCLI_PROFILE"
SCLI_CONFIG_DIR_NAME = ".scli"
DEFAULT_PROFILE_DIR = f"{str(Path.home())}/{SCLI_CONFIG_DIR_NAME}/profiles.yml"
