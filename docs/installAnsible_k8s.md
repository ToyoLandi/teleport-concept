# Deploying Kubernetes using Ansible Playbooks.

With your VMs now running and connected to the Network, its time to prepare our Virtual Machines for our Kubernetes deployment. Kubernetes has a few Host OS configurations which we will take care of in this section, notably disabling SWAP, some firewall exceptions, and installing our Container Runtime to be used by the Container Runtime Interface (CRI) later. 

Instead of doing all of this "foundational" work by running a few to many commands directly on the shell of all three nodes, we will instead leverage Ansible (a open-source IaC tool) to do the configuration for us using "playbooks". Luckily, in this repo under the 'ansible' directory you will find two pre-written playbooks (masternode-pb.yaml, workernode-pb.yaml) which will save you writing these yourself. 

Before we can run these Playbooks however, we have to install Ansible, which we will do via Python3! Lets dive in.

## Installing Ansible

Thankfully our minimal Rocky install has Python 3.12 install by default, all that is missing `pip` (pythons package manager) and an explict 'ansible' user to run our playbooks. For convenience, run the `autoAnisible.py` script located under "ansible/autoAnsible.py" in the repo to configure the Ansible "control node" and "worker-nodes".

### Using the `autoAnsible.py` Script
Fetch the Installer from the public repo
```
curl https://raw.githubusercontent.com/ToyoLandi/teleport-concept/refs/heads/main/ansible/autoAnsible.py -o autoAnsible.py
```

Run the Installer with python3 using the applicable '--control-node' or '--worker-node' arguments. 
```
# use the '--control-node' argument for the "challenger-master" node
python3 autoAnsible.py --control-node

# use the '--worker-node' argument for the "challenger-work-1" and "challenger-worker-2" nodes
python3 autoAnsible.py --worker-node
```



