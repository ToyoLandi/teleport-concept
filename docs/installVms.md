# Standing up our VMs with Rocky Linux 10.1

Happy to give Rocky a go? Here is how we configure our VM's.

1. Download the latest build of the Rocky Linux Minimal .iso from the Rocky Linux [downloads](https://rockylinux.org/download) page for your applicable CPU Architecture. The minimal .iso is 1.42 Gb for the AMD64 variant I use in this guide.
   
2. While we wait for the .iso to download, create *3* new virtual machines with the following Host Names, CPU, Ram and Disk Allocations in your Hypervisor of choice.
   
	| Host Name | CPU Cores | RAM | Disk Size |
	| ----------- | ----------- | ----- | --------- |
	| challenger-master | 2 cores | 4 GB | 20 GB |
	| challenger-worker-1 | 2 cores | 2 GB | 10 GB |
	| challenger-worker-2 | 2 cores | 2 GB | 10 GB | 

   > ⚠️ The declarations in the table above favor portability for the sake of POC/Demo deployment on a local machine (i.e Your laptop). **Its CRITICAL to note that production nodes require more resources** to handle true production load across your workloads and  Kubernetes Control-plane. 
   
3. Starting with the `challenger-master` VM, boot into your `Rocky-10.1-x86_64-minimal.iso` and select "Install Rocky Linux 10.1" using your arrow keys and Enter key to confirm your selection. 

> Note, we will repeat this Step and Step 4 below for the "challenger-worker-1" and "challenger-worker-2" nodes should you wish to deploy all three simultaneously.

4. This will launch the Rocky Guided Installer, where you can use your mouse and keyboard for further configurations. We will need to... 
   
	  A. Under "Installation Destination" > confirm the Disk Partition using the "Automatic" Storage Configuration.
	  
	  B. Under Network & Hostname > Declare the Host Name citing the table in step 2, and declare the applicable Static IP, Subnet Mask and DNS servers (if DHCP reservations are not possible) 
	  
	  C. Confirm the "Root Account" is enabled -- **Be sure you use the same root password for all three**
	  
	  D. Create the user who will be our "sudo" account for this node with a proper name (again, to prevent an anonymous user-logins with SSH) and acceptably strong password -- Be sure the "Add Administrative privileges..." box and "Require a password to use this account" box are checked.

5. Finally, Launch our Installation using the "Begin Installation" Button on the bottom right -rebooting the VM's with the "Reboot System" button once the installer completes! If you haven't already, repeat steps 3 + 4 for our other "challenger-worker-1" and "challenger-worker-2" nodes adjusting the Host Name and IP addressing as necessary. 
   
6. (IF YOU ELECTED DHCP RESERVATIONS) - It is very important to reserve the IP's fetched by the VM's during the installation before you proceed, otherwise we will face connectivity and certificate woes if our nodes fetch a different IP in the near future. 
