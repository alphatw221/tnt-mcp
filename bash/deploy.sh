#!/bin/bash

# 设置变量
IMAGE_NAME="yihsuehlin/tnt-mcp"
TAG="latest"
DEPLOYMENT_NAME="tnt-mcp" # 替换为您的 Deployment 名称
NAMESPACE="default" # 替换为您的命名空间，如果是 default 就不需要修改
POD_LABEL="app=tnt-mcp" # 替换为用于选择 pod 的标签

export PATH=$HOME/bin:$PATH

# 构建 Docker 镜像
echo "Building Docker image..."
docker build -t "$IMAGE_NAME:$TAG" -f Dockerfile .
if [ $? -ne 0 ]; then
    echo "Docker build failed."
    exit 1
fi

# 推送到 Docker Hub
echo "Pushing Docker image to Docker Hub..."
docker push "$IMAGE_NAME:$TAG"
if [ $? -ne 0 ]; then
    echo "Docker push failed."
    exit 1
fi

# 删除 Kubernetes Pod
echo "Restarting Kubernetes pod..."
kubectl delete pod -l "$POD_LABEL" -n "$NAMESPACE"
if [ $? -ne 0 ]; then
    echo "Failed to delete Kubernetes pod."
    exit 1
fi

# 检查新的 Pod 是否启动
echo "Waiting for new pod to become ready..."
kubectl rollout status deployment/"$DEPLOYMENT_NAME" -n "$NAMESPACE"
if [ $? -ne 0 ]; then
    echo "Deployment rollout failed."
    exit 1
fi

echo "Deployment completed successfully!"