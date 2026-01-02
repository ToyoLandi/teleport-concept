# Using Helm to deploy our Nginx Website w/ Cert-Manager

## Setting up Cert-Manager

We need certificates to secure our workloads running in our cluster. This is where we will use Cert-Manager enters the mix and makes our lives as Cluster Admins much easier, auto-generating and auto-renewing certs on expiration. However, we dont have the luxury of our cluster sitting on a gen-u-ine registered domain, with DNS records pointing to a real public IP in this guide, so we cannot use Certificate Authorities (CA's) like 'Let's Encrypt' or 'Cloudflare'. *Instead* we will standup our OWN CA within Cert-Manager, and deploy *self-Signed* certs for our Workoads. They may not be annoited by the holy list of "trusted CA's", but our connections will be just as secure. 

### Installing Cert-Manager
Using your user admin account > Run the follow commands to add the 'cert-manager' repo to Helm, and install cert-manager to its own `cert-manager` namespace. Be patient, it can take a minute for the Custom-Resource-Definitions (CRDs) to update on our petite VM's.
```
helm repo add jetstack https://charts.jetstack.io --force-update
helm install \
  cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --version v1.19.2 \
  --set crds.enabled=true
```
> We use the admin user for this step so we can deploy CRDs. We dont trust speezy. We do not want our normal user to manage CRD's as these are cluster wide changes + we want `cert-manager` to be in its own explict namespace.

### Set-up our Self-Signed Issuer(s) and Certificates 
Now using your 'webservers' User account (spezzy in this demo), run the following commands. 

1. Pull the `ss-issuer.yaml` and `create` to sign our self-signed CA cert
```
curl https://raw.githubusercontent.com/ToyoLandi/teleport-concept/refs/heads/main/kubernetes/cert-manager/ss-issuer.yaml -o ss-issuer.yaml

kubectl create -f ss-issuer.yaml
```
2. Pull and `create` our self-signed cert, which will get signed by our issuer above.
```
curl https://raw.githubusercontent.com/ToyoLandi/teleport-concept/refs/heads/main/kubernetes/cert-manager/ss-ca-cert.yaml -o ss-ca-cert.yaml

kubectl create -f ss-ca-cert.yaml
```

3. Pull and `create` our webservers-ca issuer to sign our server cert.
```
curl https://raw.githubusercontent.com/ToyoLandi/teleport-concept/refs/heads/main/kubernetes/cert-manager/webservers-ca-issuer.yaml -o webservers-ca-issuer.yaml

kubectl create -f webservers-ca-issuer.yaml
```

4. Pull and `create` our webservers-server cert, which will get signed by our issuer above.
```
curl https://raw.githubusercontent.com/ToyoLandi/teleport-concept/refs/heads/main/kubernetes/cert-manager/webservers-server-cert.yaml -o webservers-server-cert.yaml

kubectl create -f webservers-server-cert.yaml
```

Finally, check that our certificates are ready using the following...
```
kubectl get certificates -n webservers
```

We will use **"webservers-server-tls"** for our NGINX deployment in the next section.


## Installing NGINX
1. With our "spezzy" user, Login to `docker.io` so we can pull the "bitnami/nginx" image from docker hub.
```
helm registry login registry-1.docker.io -u <your hub.docker.com username>
```

2. Add the bitnami repo to helm.
```
helm repo add bitnami https://charts.bitnami.com/bitnami
```

3. Run the following to pull the `nginx-values.yaml`, and install `nginx` using `helm` and our defined values.yaml. This 'nginx-values.yaml' is configured too...

- Enable TLS using the "webservers-server-tls" secret.
- Deploy two replica-sets (one per node).
- Using port 80 for HTTP & 443 for HTTPS listening on our kube-vip LoadBalancer for external connections.
- Configured to check an upstream Git repo to update the Static Site
- We are using "latest" for simplicity in our deployment, though it is best practice to configure an explicit version tag for each image.

```
curl https://raw.githubusercontent.com/ToyoLandi/teleport-concept/refs/heads/main/helm/nginx-values.yaml -o nginx-values.yaml

helm install nginx-demo bitnami/nginx -f nginx-values.yaml -n webservers
```

### Checking Your Site
Run the following command to find our `EXTERNAL IP`, then navigate to this site with a browser (if your local machine shares can reach that subnet) -OR- simply `curl` the site using `https://`

```
kubectl get svc -n webservers
```

## What's Next?
An ambitious one you are. I have nothing more for you in this guide. However this is just a simple deployment, Im sure you can find some great use's for your new cluster! Just dont forget me!


## Table of Contents
1. [Standing Up our VMs with Rocky Linux 10.1](https://github.com/ToyoLandi/teleport-concept/blob/main/docs/install-vm.md)
2. [Getting Started With Ansible](https://github.com/ToyoLandi/teleport-concept/blob/main/docs/install-ansible.md)
3. [Installing Kubernetes using Ansible + Kubeadm](https://github.com/ToyoLandi/teleport-concept/blob/main/docs/install-k8s.md)
4. [Configuring a User with Kubernetes RBAC](https://github.com/ToyoLandi/teleport-concept/blob/main/docs/k8s-RBAC.md)
5. [Using Helm to deploy our Nginx Website w/ Cert-Manager](https://github.com/ToyoLandi/teleport-concept/blob/main/docs/install-nginx.md)
