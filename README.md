# README

The following is a guide to gracefully deploy a proof-of-concept, 3 node Kubernetes (aka k8s) cluster using `kubeadm` deployed via `ansible` playbooks, and securely deploy a prototype `nginx` Web Server using `flux` + `helm` within the freshly created cluster. All built on top of Rocky Linux 10.1 as our Host OS. 

This guide assumes the following...
- You have the ability to create three Virtual Machines (aka VMs) in any Hypervisor of your choice, such as VirtualBox, ProxMox or ESXi.
- You have a total of 8 GB of RAM, 40 GB of disk (preferably SSD), and 6 virtual cores available to distribute across the VM's. 
- All three Virtual Machines can reside in the same subnet, have a functional DNS server, can reach the internet, and have a virtual NIC configuration capable of providing a unique MAC address based on the [kubeadm](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/#verify-mac-address) requirements.
- You have three IP addresses available for static assignment -OR- the ability to configure DHCP reservations within the VM's destined subnet.

There are several sections to this guide, all documented under the "docs" directory to keep the README here more concise. Refer to the Table of Contents below for an ordered list of building this solution from scratch.


## Table of Contents
1. [Design Considerations](https://github.com/ToyoLandi/teleport-concept/blob/main/docs/DesignConsiderations.md)
2. [Standing Up our VMs with Rocky Linux 10.1](https://github.com/ToyoLandi/teleport-concept/blob/main/docs/installVms.md)
3. [Getting Started With Ansible](https://github.com/ToyoLandi/teleport-concept/blob/main/docs/installAnsible.md)
4. [Installing Kubernetes using Ansible + Kubeadm](https://github.com/ToyoLandi/teleport-concept/blob/main/docs/installingk8s.md)
5. [Configuring Kubernetes RBAC](link)
6. [Using Flux and Helm to deploy our Nginx Website w/ Cert-Manager](https://github.com/ToyoLandi/teleport-concept/blob/main/docs/installNginx.md)