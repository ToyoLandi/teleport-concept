# Deploying Kubernetes using Ansible Playbooks.

With your VMs now running and connected to the Network, its time to prepare our Virtual Machines for our Kubernetes deployment. Kubernetes has a few Host OS configurations which we will take care of in this section, notably disabling SWAP, some firewall exceptions, and installing our Container Runtime to be used by the Container Runtime Interface (CRI) later. 

Instead of doing all of this "foundational" work by running a few to many commands directly on the shell of all three nodes, we will instead leverage Ansible (a open-source IaC tool) to do the configuration for us using "playbooks". Luckily, in this repo under the 'ansible' directory you will find two pre-written playbooks (masternode-pb.yaml, workernode-pb.yaml) which will save you writing these yourself. 

Before we can run these Playbooks however, we have to install Ansible, which we will do via Python3! Lets dive in.

## Installing Ansible

Thankfully our minimal Rocky install has Python 3.12 install by default, all that is missing `pip` (pythons package manager) and an explict 'ansible' user to run our playbooks. For convenience we can run the `autoAnisible.py` script located under "ansible/autoAnsible.py" in the repo to configure the Ansible "control node" and "worker-nodes" -OR- run the commands below manually if you'd prefer.

### Using the `autoAnsible.py` Script
Fetch the Installer from the public repo
```
curl https://github.com/toyolandi/teleport-challenge/ansible/autoAnsible.py -o autoAnsible.py
```

Run the Installer using python3 using the applicable '--control-node' or '--worker-node' arguments. 
```
# use the '--control-node' argument for the "challenger-master" node
python3 autoAnsible.py --control-node

# use the '--worker-node' argument for the "challenger-work-1" and "challenger-worker-2" nodes
python3 autoAnsible.py --worker-node
```

### Installing Ansible Manually
First lets update our package repo, and upgrade any available packages after our recent rocky-minimal deployment using the below command **on all three nodes***... 
```
sudo dnf update -y
```

Once completed, install `pip3` (a requirement for Ansible) using the below command **on the `challenger-master` node which will double as our Ansible Control Plane**
```
sudo dnf install python3.12-pip -y
```
``
You can check `pip3` is working properly by using the command...
```
pip3 --version
```

...which should return output like...
```
pip 23.3.2 from /usr/lib/python3.12/site-packages/pip (python 3.12)
```

Finally, deploy Ansible (we use using pip3 using command...
```
pip3 install ansible --user ansible