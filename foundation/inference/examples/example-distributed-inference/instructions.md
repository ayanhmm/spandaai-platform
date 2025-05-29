# Running vLLM Across Multiple Nodes

When a single node lacks sufficient GPUs to accommodate your model, you can distribute it across multiple nodes. This guide explains how to set up and run vLLM in a multi-node environment.

## Prerequisites

- Ensure identical execution environments across all nodes (same model path and Python environment).
- Docker is recommended to maintain consistency and manage host machine differences.
- High-speed network connectivity between nodes (preferably Infiniband) for optimal performance.

## Setting Up the Cluster

### On the Head Node
Execute the following command:
```bash
bash run_cluster.sh \
                vllm/vllm-openai \
                ip_of_head_node \
                --head \
                /path/to/the/huggingface/home/in/this/node \
                -e VLLM_HOST_IP=ip_of_this_node
```

### On Each Worker Node
Run the following command:
```bash
bash run_cluster.sh \
                vllm/vllm-openai \
                ip_of_head_node \
                --worker \
                /path/to/the/huggingface/home/in/this/node \
                -e VLLM_HOST_IP=ip_of_this_node
```

### Important Notes:
- Keep all command shells active to maintain the cluster.
- Use actual IP addresses accessible to all nodes.
- Each worker node needs a unique `VLLM_HOST_IP`.

## Accessing and Verifying the Cluster

### Enter Any Node's Container:
```bash
docker exec -it node /bin/bash
```

### Verify Cluster Status:
```bash
ray status
```

## Running vLLM

You can configure vLLM in two ways:

### Option 1: Using Both Tensor and Pipeline Parallelism
For example, with 16 GPUs across 2 nodes (8 GPUs per node):
```bash
vllm serve /path/to/the/model/in/the/container \
     --tensor-parallel-size 8 \
     --pipeline-parallel-size 2
```

### Option 2: Using Only Tensor Parallelism
For the same 16 GPU setup:
```bash
vllm serve /path/to/the/model/in/the/container \
     --tensor-parallel-size 16
```

## Performance Optimization

### For Infiniband Setup:
- Add `--privileged -e NCCL_IB_HCA=mlx5` to the `run_cluster.sh` script.
- Verify Infiniband usage by running:
```bash
NCCL_DEBUG=TRACE vllm serve ...
```

Look for:
- `[send] via NET/IB/GDRDMA` (optimal)
- Avoid `[send] via NET/Socket` (suboptimal)

## Important Considerations

### Model Accessibility:
- Download the model to all nodes using identical paths, or
- Use a distributed file system accessible to all nodes.

### Using Hugging Face Models:
- Add your token to the cluster script:
```bash
-e HF_TOKEN=your_token_here
```
- Preferably download models beforehand and use local paths.

### Environment Variables:
- Set them during cluster creation through `run_cluster.sh`.
- Example:
```bash
-e NCCL_SOCKET_IFNAME=eth0
```
- Avoid setting variables in individual shells.

### GPU-GPU Communication
Always verify GPU-GPU communication between nodes before running intensive tasks.

This setup enables efficient distributed model serving across multiple nodes while maintaining optimal performance through proper configuration and communication channels.

