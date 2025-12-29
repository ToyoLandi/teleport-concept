# Installing Kubernetes using Ansible + Kubeadm

We should now have a 'ansible' non-root user, which can connect to all three nodes (our soon to be k8s control-plane and two worker nodes) using a custom certificate. Now we can use Ansible Playbooks to quickly...

- Disable Swap and SELinux as requested by the [kubeadm](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/) docs.
- Install containerd, runc, + configure the containerd to use systemd as its cgroup driver.
- Configure kernel host, and firewall networking configurations to prepare for k8s.
- Importantly, Install kubeadm, kubelet, and kubectl.

1. `curl` the "install-k8s.yaml" playbook file from this repos "ansible" directory, 
```
curl https://raw.githubusercontent.com/ToyoLandi/teleport-concept/refs/heads/main/ansible/install-k8s.yaml -o ~/ansible/install-k8s.yaml 
```
> This a great reference to see all the commands we use to config/deploy k8s in once place.

3. Begin our kubernetes deployment by running the following ansible-playbook command. Thanks to the `-K` [argument](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_privilege_escalation.html#using-become) you will be prompted for the `BECOME password`, aka the password of your root account, without needing to expose this in your playbook or command history. 
```
ansible-playbook -i ~/ansible/hosts.yaml ~/ansible/install-k8s.yaml -K
```

Once complete, all three nodes are ready to run `kubeadm` commands. 