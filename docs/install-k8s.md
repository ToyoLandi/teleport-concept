# Installing Kubernetes Using Ansible + Kubeadm

We should now have a 'ansible' non-root user, which can connect to all three nodes (our soon to be k8s control-plane and two worker nodes) using a custom certificate. Now we can use Ansible Playbooks to quickly...

- Disable Swap and SELinux as requested by the [kubeadm](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/) docs.
- Install containerd, runc, + configure the containerd to use systemd as its cgroup driver.
- Configure kernel, host, and firewall networking configurations to prepare for k8s.
- Deploy kube-vip in --service mode for on-prem loadbalancing via ARP.
- Importantly, Install kubeadm, kubelet, and kubectl.

### Before You Run The Playbooks...
**VERY IMPORTANT...** Modify the "host.yaml" Host IP address and kube-vip address to match your environment. The `kube_vip_range` will be used as the "EXTERNAL IP" of your exposed Kubernetes Services such as the NGINX Site later in this guide. This range must be available on your local network and ideally preserved from your available DHCP pool.

## Part 1 : Setting the Stage for Kubernetes Using Ansible.

1. From your 'ansible' users terminal, `curl` the "stage-k8s.yaml" playbook "ansible" directory, 
```
curl https://raw.githubusercontent.com/ToyoLandi/teleport-concept/refs/heads/main/ansible/playbooks/stage-k8s.yaml -o ~/ansible/stage-k8s.yaml 
```
> The 'stage-k8s' playbook is a great reference to see all the commands we use to config/deploy the k8s requirements, in once place.

2. Stage our Kubernetes deployment by running the following ansible-playbook command. Thanks to the `-K` [argument](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_privilege_escalation.html#using-become) you will be prompted for the `BECOME password`, aka the password of your root account, without needing to expose this in your playbook or command history. 
```
ansible-playbook -i ~/ansible/hosts.yaml ~/ansible/stage-k8s.yaml -K
```

Once complete, all three nodes are ready for actual Kubernetes deployment in the next section! 

## Part 2 : Initalizing Our Control-plane and Joining our Worker Nodes

Here we truly deploy our Kubernetes Stack using `kubeadm` and `kubectl` commands using the 'init-k8s' playbook. 

1.  From the 'ansible' user shell, `curl` the kubeadm-conf.j2 kubeadm config template and init-k8s.yaml playbook to our '~/ansible' dir. 
```
curl https://raw.githubusercontent.com/ToyoLandi/teleport-concept/refs/heads/main/ansible/playbooks/init-k8s.yaml -o ~/ansible/init-k8s.yaml
curl https://raw.githubusercontent.com/ToyoLandi/teleport-concept/refs/heads/main/kubernetes/conf/kubeadm-conf.j2 -o ~/ansible/kubeadm-conf.j2
```
2. Run our 'init-k8s' playbook to initialize our Cluster, and join our workers. 
```
ansible-playbook -i ~/ansible/hosts.yaml ~/ansible/init-k8s.yaml -K
```

### Removing the Kubernetes Deployment
If something went awry during the install, or you wish to tweak the configuration files and redeploy Kubernetes, run the following commands. 
```
curl https://raw.githubusercontent.com/ToyoLandi/teleport-concept/refs/heads/main/ansible/playbooks/remove-k8s.yaml -o ~/ansible/remove-k8s.yaml
```
```
ansible-playbook -i ~/ansible/hosts.yaml ~/ansible/remove-k8s.yaml -K
```
> If your deployment failed royally before the CNI interfaces could be configured, its expected the second step will fail in Ansible, since there are no interfaces to remove.

## Running `kubectl` Commands with Admin Permissions
1. Run the below commands on any user you wish to run unrestricted kubectl commands with shell access to our Master node (challenger-master)
```
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```
> In this guide, only the "challenger-master" node has `kubectl` installed, but this isnt the only possible way. You could even install `kubectl` on your local machine as long as you have the ability to reach the API server URL and a config file present, you can run kubernetes commands. 

## What's Next?
Congratulations, you are officially a Kubernetes Cluster Admin! Now the real fun begins configuring RBAC rules, standing up our nginx workload using a normal user with limited permissions, and a touch of certificate tomfoolery. Proceed to [Configuring a User with Kubernetes RBAC](https://github.com/ToyoLandi/teleport-concept/blob/main/docs/k8s-RBAC.md) when your ready. 


## Table of Contents
1. [Standing Up our VMs with Rocky Linux 10.1](https://github.com/ToyoLandi/teleport-concept/blob/main/docs/install-vms.md)
2. [Getting Started With Ansible](https://github.com/ToyoLandi/teleport-concept/blob/main/docs/install-ansible.md)
3. [Installing Kubernetes using Ansible + Kubeadm](https://github.com/ToyoLandi/teleport-concept/blob/main/docs/install-k8s.md)
4. [Configuring a User with Kubernetes RBAC](https://github.com/ToyoLandi/teleport-concept/blob/main/docs/k8s-RBAC.md)
5. [Using Helm to deploy our Nginx Website w/ Cert-Manager](https://github.com/ToyoLandi/teleport-concept/blob/main/docs/install-nginx.md)
