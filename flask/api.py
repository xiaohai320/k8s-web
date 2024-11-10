

import requests
from flask import Flask, request, jsonify, abort
from kubernetes import client, config
from flask_cors import CORS
from kubernetes.client import ApiException


app = Flask(__name__)
CORS(app)
# 加载 Kubernetes 配置
config.load_kube_config(config_file='../config')

# 创建 Kubernetes API 客户端
apps_v1 = client.AppsV1Api()
core_v1 = client.CoreV1Api()

# 创建 Deployment
@app.route('/deployments', methods=['POST'])
def create_deployment():
    data = request.json
    namespace = data.get('namespace')
    deployment_name = data.get('name')
    container_image = data.get('image')

    if not namespace or not deployment_name or not container_image:
        return jsonify({"error": "Missing required fields"}), 400

    deployment = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": deployment_name,
            "namespace": namespace
        },
        "spec": {
            "replicas": 1,
            "selector": {
                "matchLabels": {
                    "app": deployment_name
                }
            },
            "template": {
                "metadata": {
                    "labels": {
                        "app": deployment_name
                    }
                },
                "spec": {
                    "containers": [
                        {
                            "name": deployment_name,
                            "image": container_image,
                            "ports": [
                                {
                                    "containerPort": 80
                                }
                            ]
                        }
                    ]
                }
            }
        }
    }
    try:
        response = apps_v1.create_namespaced_deployment(namespace, deployment)
        return jsonify({"message": "Deployment created", "response": response.to_dict()}), 201
    except client.exceptions.ApiException as e:
        return jsonify({"error": str(e)}), 500

# 列出 Deployment
@app.route('/deployments', methods=['GET'])
def list_deployments():
    namespace = request.args.get('namespace', 'default')
    try:
        deploys = apps_v1.list_namespaced_deployment(namespace)
        return jsonify([deploy.to_dict() for deploy in deploys.items]), 200
    except client.exceptions.ApiException as e:
        return jsonify({"error": str(e)}), 500

# 更新 Deployment
@app.route('/deployments/<string:namespace>/<string:name>', methods=['PUT'])
def update_deployment(namespace, name):
    data = request.json
    container_image = data.get('image')

    if not container_image:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        deployment = apps_v1.read_namespaced_deployment(name, namespace)
        deployment.spec.template.spec.containers[0].image = container_image
        response = apps_v1.patch_namespaced_deployment(name, namespace, deployment)
        return jsonify({"message": "Deployment updated", "response": response.to_dict()}), 200
    except client.exceptions.ApiException as e:
        return jsonify({"error": str(e)}), 500

# 删除 Deployment
@app.route('/deployments/<string:namespace>/<string:name>', methods=['DELETE'])
def delete_deployment(namespace, name):
    try:
        response = apps_v1.delete_namespaced_deployment(
            name,
            namespace,
            body=client.V1DeleteOptions(
                propagation_policy='Foreground',
                grace_period_seconds=5
            )
        )
        return jsonify({"message": "Deployment deleted", "response": response.to_dict()}), 200
    except client.exceptions.ApiException as e:
        return jsonify({"error": str(e)}), 500
#获取pods
@app.route('/pods', methods=['GET'])
def list_pods():
    namespace = request.args.get('namespace', 'default')  # 默认命名空间为 'default'
    try:
        pods = core_v1.list_namespaced_pod(namespace)
        return jsonify([pod.to_dict() for pod in pods.items]), 200
    except client.exceptions.ApiException as e:
        return jsonify({"error": str(e)}), 500

#扩缩容replicas
@app.route('/scale-pods', methods=['POST'])
def scale_pods():
    # 获取请求参数
    namespace = request.json.get('namespace', 'default')  # 默认命名空间为 'default'
    deployment_name = request.json.get('deployment_name')
    replicas = request.json.get('replicas')

    if not deployment_name or not replicas:
        return jsonify({"error": "缺少必要参数: deployment_name and replicas"}), 400

    try:
        # 获取现有的Deployment对象
        deployment = apps_v1.read_namespaced_deployment(name=deployment_name, namespace=namespace)

        # 更新副本数
        deployment.spec.replicas = int(replicas)

        # 应用更改
        api_response = apps_v1.patch_namespaced_deployment(name=deployment_name, namespace=namespace, body=deployment)
        print(api_response.to_dict())
        return jsonify({"message": f"Deployment '{deployment_name}' scaled to {replicas} replicas", "deployment": api_response.to_dict()}), 200

    except ApiException as e:
        return jsonify({"error": str(e)}), 500

#获取指定deployment的详情，扩缩容后刷新使用
@app.route('/deployments/<string:namespace>/<string:deployment_name>', methods=['GET'])
def get_deployment(namespace, deployment_name):
    try:
        # 查询指定的 Deployment
        deployment = apps_v1.read_namespaced_deployment(name=deployment_name, namespace=namespace)
        # 将 Deployment 转换为字典
        deployment_dict = deployment.to_dict()
        return jsonify(deployment_dict)
    except client.exceptions.ApiException as e:
        if e.status == 404:
            abort(404, description="Deployment not found")
        else:
            abort(500, description=str(e))
    except Exception as e:
        abort(500, description=str(e))
# get nodes
@app.route('/nodes', methods=['GET'])
def list_nodes():
    name = request.args.get('name')  # 获取请求参数中的节点名称，默认为 None
    try:
        if name:
            # 如果提供了节点名称，则获取指定节点的信息
            node = core_v1.read_node(name)
            return jsonify(node.to_dict()), 200
        else:
            # 否则，获取所有节点的信息
            nodes = core_v1.list_node()
            return jsonify([node.to_dict() for node in nodes.items]), 200
    except client.exceptions.ApiException as e:
        # 处理API异常
        return jsonify({"error": str(e)}), 500
@app.route('/svc',methods=['GET'])
def list_svc():
    namespace=request.args.get('namespace')
    pod_label = request.args.get('label','')
    try:
        svc=core_v1.list_namespaced_service(namespace,label_selector=pod_label)
        print(jsonify([svc.to_dict() for svc in svc.items]))
        return jsonify([svc.to_dict() for svc in svc.items]),200
    except client.exceptions.ApiException as e:
        return jsonify({"error":"error"}),500
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)