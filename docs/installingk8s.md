# Installing Kubernetes using Ansible + Kubeadm

We should now have a 'ansible' non-root user, which can connect to all three nodes (our soon to be k8s control-plane and two worker nodes) using a custom certificate. Now we can use Ansible Playbooks to quickly...

- Disable Swap and SELinux as requested by the [kubeadm](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/) docs.
- Install containerd, runc, + configure the containerd to use systemd as its cgroup driver.
- Configure kernel host, and firewall networking configurations to prepare for k8s.
- Importantly, Install kubeadm, kubelet, and kubectl.

## Setting the Stage for Kubernetes using Ansible.

1. From your 'ansible' users terminal, `curl` the "install-k8s.yaml" playbook from this repos "ansible" directory, 
```
curl https://raw.githubusercontent.com/ToyoLandi/teleport-concept/refs/heads/main/ansible/stage-k8s.yaml -o ~/ansible/stage-k8s.yaml 
```
> This a great reference to see all the commands we use to config/deploy k8s in once place.

3. Begin our kubernetes deployment by running the following ansible-playbook command. Thanks to the `-K` [argument](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_privilege_escalation.html#using-become) you will be prompted for the `BECOME password`, aka the password of your root account, without needing to expose this in your playbook or command history. 
```
ansible-playbook -i ~/ansible/hosts.yaml ~/ansible/stage-k8s.yaml -K
```

Once complete, all three nodes are ready to run the `kubeadm` commands used by the playbook in the next section. 

## Initalizing our Control-plane and Joining our Worker nodes

Here we take the first steps in building our Kubernetes Stack using `kubeadm` and `kubectl` commands using our 'init-k8s' playbook. 

By the end of this section, we will...
- Have a working Kubernetes Control-Plane running on our "Challenger-master" node.
- Have Flannel (our Pod network add-on of choice for this demo) configured and running
- Our worker-nodes (challenger-worker-1, challenger-worker-2) joined to the cluster
- The ability to run `kubectl` commands on your own to start playing with kubeapi.

1.  From the 'ansible' user shell, `curl` the kubeadm-conf.j2 kubeadm config template and init-k8s.yaml playbook to our '~/ansible' dir. 
```
curl https://raw.githubusercontent.com/ToyoLandi/teleport-concept/refs/heads/main/ansible/init-k8s.yaml -o ~/ansible/init-k8s.yaml
curl https://raw.githubusercontent.com/ToyoLandi/teleport-concept/refs/heads/main/ansible/kubeadm-conf.j2 -o ~/ansible/kubeadm-conf.j2
```
2. Run our 'init-k8s' playbook to initilize our Cluster, and join our workers. 
```
ansible-playbook -i ~/ansible/hosts.yaml ~/ansible/init-k8s.yaml -K
```
3. As a final-step, run the below commands on any user you wish to run kubectl commands with shell access to our Master node (challenger-master)

```
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

## Whats next?
Congratulations, you are offically a Kubernetes Cluster Admin! Now the real fun begins configuring RBAC rules, standing up our nginx workload using a normal user with limited permissions, and a touch of certificate tomfoolery. Proceede to our "installNginx" doc when your ready. 