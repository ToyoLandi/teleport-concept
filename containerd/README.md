# README

The `config.toml` file stored here is the default containerd config.toml generated using the `containerd config default` command on a containerd installed node - *with one important edit to enable the use of the systemd cgroup driver* as defined in the [kubeadm](https://kubernetes.io/docs/setup/production-environment/container-runtimes/#containerd) docs. 

This change is made on line 109

Example:
```
          [plugins.'io.containerd.cri.v1.runtime'.containerd.runtimes.runc.options]
            BinaryName = ''
            CriuImagePath = ''
            CriuWorkPath = ''
            IoGid = 0
            IoUid = 0
            NoNewKeyring = false
            Root = ''
            ShimCgroup = ''
            SystemdCgroup = true
```

The [install-k8s.yaml](https://github.com/ToyoLandi/teleport-concept/blob/main/ansible/install-k8s.yaml) Ansible playbook will pull this config.toml via `curl` to automatically apply this config during k8s node init. 

### Additional References: 
- https://github.com/containerd/containerd/tree/main
- https://kubernetes.io/docs/setup/production-environment/container-runtimes/#containerd 
- https://systemd.io/CONTAINER_INTERFACE/