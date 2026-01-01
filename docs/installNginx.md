# TODO


## Deploying Traefik as our Reverse Proxy

We have our Cluster listening on the same IP we configured on our Virtual Machine. But if we want to deploy a website running on all two worker nodes with different IPs, how will we loadBalance our traffic to take advantage of the *cluster*? This is where we will use Traefik. 

### Installing Traefik with Helm

Using your Kubernetes Admin account > Run the following commands to add the traefik repo to Helm 
```
helm repo add traefik https://traefik.github.io/charts --force-update
kubectl create namespace traefik
```


## Setting up Cert-Manager

We need certificates to secure our workloads running in our cluster. This is where we will use Cert-Manager enters the mix and makes our lives as Cluster Admins much easier, auto-generating and auto-renewing certs on expiration. However, we dont have the luxury of our cluster sitting on a gen-u-ine registered domain, with DNS records pointing to a real public IP in this guide, so we cannot use Certificate Authorities (CA's) like 'Let's Encrypt' or 'Cloudflare'. *Instead* we will standup our OWN CA within Cert-Manager, and deploy *self-Signed* certs for our Workoads. They may not be annoited by the holy list of "trusted CA's", but our connections will be just as secure. 

### Installing Cert-Manager
Using your Kubernetes Admin account > Run the follow commands to add the 'cert-manager' repo to Helm, and install cert-manager to its own `cert-manager` namespace. Be patient, it can take a few minutes for the Custom-Resource-Definitions (CRDs) to update on our petite VM's.
```
helm repo add jetstack https://charts.jetstack.io --force-update
helm install \
  cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --version v1.19.2 \
  --set crds.enabled=true
```

## Installing NGINX


```
helm registry login registry-1.docker.io -u <your hub.docker.com username>
curl <values.yaml>
helm install nginx-demo bitnami/nginx -f nginx-values.yaml
```