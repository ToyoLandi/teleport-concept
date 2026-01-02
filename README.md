# README

The repo is a guide to gracefully deploy a proof-of-concept, 3 node Kubernetes (aka k8s) cluster using `kubeadm` deployed via `ansible` playbooks, and securely deploy a prototype `nginx` Web Server + `cert-manager` using `helm` within the freshly created cluster. 

Included in this repo is a custom python3 script to easily setup Ansible on all three nodes named [autoAnsible.py](https://github.com/ToyoLandi/teleport-concept/blob/main/ansible/autoAnsible.py) as well as custom Ansible playbooks to install and remove Kubernetes, so you dont have to write these yourself.

### This Guide Assumes...
- You have the ability to create three Virtual Machines (aka VMs) in any Hypervisor of your choice, such as VirtualBox, ProxMox or ESXi.
- You have a total of 8 GB of RAM, 40 GB of disk (preferably SSD), and 6 virtual cores available to distribute across the VM's. 
- All three Virtual Machines can reside in the same subnet, have a functional DNS server, can reach the internet, and have a virtual NIC configuration capable of providing a unique MAC address based on the [kubeadm](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/#verify-mac-address) requirements.
- You have Four IP addresses available for static assignment -OR- the ability to configure DHCP reservations within the VM's destined subnet, as well as a small range of IP address for our Load Balancer pool
- You CANNOT have your cluster facing the internet (no public IP).
- You CANNOT configure DNS A or AAAA records.
- You DO NOT have an existing Certificate Authority available to use.

### How To Use This Repo...
There are several sections to this guide intended to be followed in order, all documented under the "docs" directory to keep the README here more concise. If something isnt making sense, check the previous page in case you overlooked a step or note. Refer to the Table of Contents below for an ordered list of building this solution from scratch.

## Table of Contents
1. [Standing Up our VMs with Rocky Linux 10.1](https://github.com/ToyoLandi/teleport-concept/blob/main/docs/install-vm.md)
2. [Getting Started With Ansible](https://github.com/ToyoLandi/teleport-concept/blob/main/docs/install-ansible.md)
3. [Installing Kubernetes using Ansible + Kubeadm](https://github.com/ToyoLandi/teleport-concept/blob/main/docs/install-k8s.md)
4. [Configuring a User with Kubernetes RBAC](https://github.com/ToyoLandi/teleport-concept/blob/main/docs/k8s-RBAC.md)
5. [Using Helm to deploy our Nginx Website w/ Cert-Manager](https://github.com/ToyoLandi/teleport-concept/blob/main/docs/install-nginx.md)