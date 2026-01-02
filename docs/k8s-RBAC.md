# Configuring a User with Kubernetes RBAC

What if we want other users (Devs, App Owners, etc) to have the freedom to deploy workloads in an assigned namespace, but we dont want them to be able to break our entire Kubernetes deployment? This is where K8s RBAC comes in handy. 

As an example, lets create a "user" named 'spezzy' in the 'webdevs' group and limit them to the "webserver" namespace but allow them to create and remove workloads in "webserver", using the "webserver-admin" Role and RoleBinding

### A Quick Review of Kubernetes RBAC Design

The concept of a "user" in Kubernetes is not what you typically expect, we dont create an explict user named "spezzy". We actually create a **certificate** with the Common Name (CN) declaring our username, and the Organization(O) declaring any groups this "user" is a member of. This certificate is presented to the kubeapi-server when running `kubectl` commands - which will check the applicable roles associated with the 'CN' and 'O' values within the certificate. If "spezzy" is trying to do actions outside scope (like making changes in another namespace), the command is blocked from exec by kubeapi-server with a `Error from server (Forbidden):...` message. 

Earlier, When you stood up your admin account and ran those commands to write that "~.kube/config" file, you actually copied the kubernetes 'config' file which contains the Certificate data for the "kubernetes-admin" account.

> There are other methods of mapping a "user" to their Role(s) or ClusterRole(s) such as bearer tokens, but those are out of scope of this guide and better described by the [Kubernetes RBAC docs](https://kubernetes.io/docs/reference/access-authn-authz/authentication/).


## Creating our Namespace
open a shell with our admin 'kubectl' account and run the following command...
```
kubectl create namespace webservers
```
Thats it! 


## Configuring our Role and RoleBinding

From your 'sudo' account terminal, `curl` the role and roleBinding down from the repo, prepopulated for "spezzy" in this example. 
```
curl https://raw.githubusercontent.com/ToyoLandi/teleport-concept/refs/heads/main/kubernetes/rbac/role.yaml -o role.yaml
curl https://raw.githubusercontent.com/ToyoLandi/teleport-concept/refs/heads/main/kubernetes/rbac/roleBinding.yaml -o roleBinding.yaml
```
> If you are using these are *templates* be sure to modify the values within the role and roleBinding to match your deployment. 

And apply this role and Rolebinding using `kubectl`
```
kubectl apply -f role.yaml
kubectl apply -f roleBinding.yaml
```

## Generating our User Certificate

First, open a shell with your 'sudo' account. 

Generate a private key for our user, replacing the <user> brackets with their username.
```
openssl genrsa -out spezzy.key
```
Then create a CSR with our key, declaring the username and group in the CN and O fields...
```
openssl req -new -key spezzy.key -out spezzy.csr -subj "/CN=spezzy/O=webdevs"
```
Then using your CA certificate and key generated automatically by `kubeadm` under '/etc/kubernetes/pki/ca.crt' and 'etc/kubernetes/pki/ca.key', sign the CSR, setting an expiration using `-days 365`...
```
sudo openssl x509 -req -in spezzy.csr -CA /etc/kubernetes/pki/ca.crt -CAkey /etc/kubernetes/pki/ca.key -CAcreateserial -out spezzy.crt -days 365
```
You now have a user cert named 'spezzy.crt' ready to be converted to BASE64 for use in our kubectl config file we are about to create! 


## Making the kubectl-config File

From the same 'sudo' account user, curl the template file from the repo so we can make our edits...
```
curl https://raw.githubusercontent.com/ToyoLandi/teleport-concept/refs/heads/main/kubernetes/rbac/kubeconfig-template -o kubeconfig-template.yaml
```
> Alternatively, you can `cp` and edit using `vi` the current kubernetes-admin config under '~/.kube/config'

Using `vi` or `nano`, edit the values in CAPS to their proper values, and save the config. The X_BASE64 cert values can be generated using the below commands. 
```
echo "$(cat /etc/kubernetes/pki/ca.crt)" | base64 -w 0
```
```
echo "$(cat spezzy.crt)" | base64 -w 0
```
```
echo "$(cat spezzy.key)" | base64 -w 0
```
> I like to copy these to a local notepad on my local machine to make this a little easier - **BE SURE YOUR BASE64 STRINGS ARE ON ONE LINE**

The CLUSTER_NAME can be fetched using... the default used in this guide is "kubernetes"
```
kubectl config view --minify -o jsonpath='{.clusters[].name}'
```
The last step is to copy the kubectl-config.yaml file to '~/.kube/config' for the user. If you wish to keep your sudo account with Admin access, you can create a new user with `useradd -m` and `mkdir ~/.kube` before copying -OR- you can run the commands under [Running `kubectl` Commands with Admin Permissions] in the "installingK8s" to restore your Admin access.
```
sudo useradd -m spezzy
sudo passwd spezzy
sudo mkdir /home/spezzy/.kube
sudo cp kubeconfig-template /home/spezzy/.kube/config
```

## Testing Our New User
Jump over to "spezzy's" terminal and lets try to run some `kubectl` commands.
```
su spezzy
```
Then try to run `get pods` against ALL namespaces - this should get blocked.
```
kubectl get pods -A
```
Now try to run the same just for our webservers group - We should get "No resources found in webservers namespace." This means we are limited to webservers like we expect!
```
kubectl get pods -n webservers
```

`helm` will inherit your permissions from your kubeconfig which you can test with the below, which will return an empty list... for now.
```
helm list -n webservers
```

## What's Next?
We now have a new kubernetes user (spezzy) that is scoped to the new 'webservers' namespace, but have no web servers! Proceed to the [Using Helm to deploy our Nginx Website w/ Cert-Manager](https://github.com/ToyoLandi/teleport-concept/blob/main/docs/install-nginx.md) section and give spezzy some work to do by configuring NGINX with cert-manager.


## Table of Contents
1. [Standing Up our VMs with Rocky Linux 10.1](https://github.com/ToyoLandi/teleport-concept/blob/main/docs/install-vms.md)
2. [Getting Started With Ansible](https://github.com/ToyoLandi/teleport-concept/blob/main/docs/install-ansible.md)
3. [Installing Kubernetes using Ansible + Kubeadm](https://github.com/ToyoLandi/teleport-concept/blob/main/docs/install-k8s.md)
4. [Configuring a User with Kubernetes RBAC](https://github.com/ToyoLandi/teleport-concept/blob/main/docs/k8s-RBAC.md)
5. [Using Helm to deploy our Nginx Website w/ Cert-Manager](https://github.com/ToyoLandi/teleport-concept/blob/main/docs/install-nginx.md)
