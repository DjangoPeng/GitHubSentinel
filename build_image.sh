#!/bin/bash

# 获取当前的 Git 分支名称
BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD)

# 如果需要，可以处理分支名称，例如替换无效字符
BRANCH_NAME=${BRANCH_NAME//\//-}

# 使用 Git 分支名称作为 Docker 镜像的标签
IMAGE_TAG="github_sentinel:${BRANCH_NAME}"

# 构建 Docker 镜像
docker build -t $IMAGE_TAG .

# 输出构建结果
echo "Docker 镜像已构建并打上标签: $IMAGE_TAG"