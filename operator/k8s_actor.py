from kubernetes import client, config
import time

class KubernetesActor:
    def __init__(self, namespace="default"):
        config.load_incluster_config()
        self.apps_v1 = client.AppsV1Api()
        self.namespace = namespace

    def get_replicas(self, deployment_name):
        try:
            deployment = self.apps_v1.read_namespaced_deployment(deployment_name, self.namespace)
            return deployment.spec.replicas
        except Exception as e:
            print("ERROR getting replicas: " + str(e))
            return 0

    def scale_deployment(self, deployment_name, replicas):
        try:
            current = self.get_replicas(deployment_name)
            if current == replicas:
                print("Already at " + str(replicas) + " replicas")
                return True
            scale = self.apps_v1.read_namespaced_deployment_scale(deployment_name, self.namespace)
            scale.spec.replicas = replicas
            self.apps_v1.replace_namespaced_deployment_scale(deployment_name, self.namespace, scale)
            print("Scaled " + deployment_name + " from " + str(current) + " to " + str(replicas))
            return True
        except Exception as e:
            print("ERROR scaling: " + str(e))
            return False

    def restart_deployment(self, deployment_name):
        try:
            body = {"spec": {"template": {"metadata": {"annotations": {"kubectl.kubernetes.io/restartedAt": str(time.time())}}}}}
            self.apps_v1.patch_namespaced_deployment(deployment_name, self.namespace, body)
            print("Restarted " + deployment_name)
            return True
        except Exception as e:
            print("ERROR restarting: " + str(e))
            return False
