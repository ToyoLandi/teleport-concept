# Kubernetes RBAC

What if we want other users (Devs, App Owners, etc) to have the freedom to deploy workloads in an assigned namespace, but we dont want them to be able to break our entire Kubernetes deployment? This is where K8s RBAC comes in handy. 

As an example, lets create a "user" named 'spezzy' and limit them to the "webserver" namespace but allow them to create and remove workloads in "webserver", using the "webserver-admin" Role.

### A Quick Review of Kubernetes RBAC Design

The concept of a "user" in Kubernetes is not what you typically expect, we dont create an explict user named "spezzy". We actually create a **certificate** with the Common Name (CN) declaring our username, and the Organization(O) declaring any groups this "user" is a member of. This certificate is presented to the kubeapi-server when running `kubectl` commands - which will check the applicable ClusterRole(s) associated with the CN and O values within the certificate. If "spezzy" is trying to do actions that our outside of their ClusterRole scope (like making changes in another namespace), the command is blocked from exec by kubeapi-server. 

Earlier, When you stood up your admin account and ran those commands to write that "~.kube/config" file, you actually copied the 'kubernetes-admin' config file which contains the 'client-certificate-data' we are alluding too.

> There are other methods of mapping a "user" to their Role(s) or ClusterRole(s) such as bearer tokens, but those are out of scope of this guide and better described by the [Kubernetes RBAC docs](https://kubernetes.io/docs/reference/access-authn-authz/authentication/).

## Generating our User Certificate

