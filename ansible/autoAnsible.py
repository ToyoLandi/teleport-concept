# Python3 Script for Demo Ansible Auto configuration. 
# 
# This script is NOT intended for production use though I have taken the
# the effort to ensure the commands called can fail safely under a few common
# scenarios. 
# 
# This script should be called by a 'root'/'wheel' user -- we will handle user
# context within the script running commands under the created 'ansible' user
# where nessicary. 

import os
import sys
import getpass
import subprocess

def create_user(): 
    '''
    This should be ran as 'root'.

    Creates an explict 'ansible' user to be used for Ansible interactions such
    as running playbooks.
    '''
    print("autoAnsible: Creating explict 'ansible' user")
    # We could accept user input here for a username besides 'ansible' but for
    # the sake of the demo, lets keep this username explict. 
    username = 'ansible'

    # Check if user already exist on the node.
    try:
        subprocess.run(['id', username], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"autoAnsible: User '{username}' already exists.")
        return
    except subprocess.CalledProcessError:
        # User does not exist, proceed with creation
        pass

    password = getpass.getpass("autoAnsible: Enter password for 'ansible' user: ").strip()
    
    try:
        print(f"autoAnsible: Creating user '{username}'...")
        # Create user with a home directory
        subprocess.run(['useradd', username, '-m'], check=True)
        # Set the password using chpasswd (more secure)
        # chpasswd expects input in the format "username:password"
        process = subprocess.Popen(['chpasswd'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate(input=f"{username}:{password}")
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, 'chpasswd', stderr)
        print(f"autoAnsible: User '{username}' created successfully.")

    except subprocess.CalledProcessError as e:
        print(f"autoAnsible: [!] Failed to create user: {e.stderr if hasattr(e, 'stderr') else e}")
        # TODO - Handle cleanup without checking home dir, as home dir is not being created
        # Clean up if useradd succeeded but chpasswd failed
        if os.path.exists(f"/home/{username}"):
            subprocess.run(['userdel', '-r', username])
            print(f"autoAnsible: [*] Rolled back user creation for '{username}'.")
        sys.exit(1)

def update_pkg_manager():
    '''
    This should be ran as 'root'

    Runs the `dnf update -y` process on the host OS shell. 
    '''
    print('autoAnsible: Updating package manager repo')
    # TODO - check host os package manager in use (dnf, yum, apt-get) & update
    process = subprocess.Popen(['dnf', 'update', '-y'], text=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    stdout, stderr = process.communicate()
    print(stdout)
    if process.returncode != 0: 
        raise subprocess.CalledProcessError(process.returncode, 'dnf', stderr)

def install_pip():
    '''
    This should be ran using the 'root' user.

    Runs the `dnf install python3.12-pip -y` process on the host OS shell. 
    '''
    print("autoAnsible: Installing [pip] via dnf")
    pkg = 'python3.12-pip'
    process = subprocess.Popen(['dnf', 'install', pkg, '-y'], text=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    stdout, stderr = process.communicate()
    print(stdout)
    if process.returncode != 0: 
        raise subprocess.CalledProcessError(process.returncode, 'dnf', stderr)

def install_ansible(user:str):
    '''
    This should be ran using the 'ansible' user.

    Runs the `pip3 install ansible-core --user` process on the host OS shell. 
    '''
    # First, install ansible-core via pip for the 'ansible' user. Since this
    # script is initalized using sudo, we need to change our user context then
    # execute the pip install. We use 'su {user} -c ...' to do so.
    print("autoAnsible: Installing [ansible-core] via pip for 'ansible' user")
    su_command = 'python3 -m pip install --user ansible-core'
    process = subprocess.Popen(['su', user, '-c', su_command], text=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    stdout, stderr = process.communicate()
    print(stdout)
    if process.returncode != 0: 
        print('autoAnsible: ERROR during ansible-core installation.')
        raise subprocess.CalledProcessError(process.returncode, 'su', stderr)
    
    # Additionally, we need to create the '/home/ansible/ansible' directory since we
    # used pip to install with our ansible user, we were unable to write to the
    # default location of "/etc/ansible". 
    print("autoAnsible: creating Ansible directory in 'ansible' user-space.")
    su_command = 'mkdir $HOME/ansible'
    process = subprocess.Popen(['su', user, '-c', su_command], text=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    stdout, stderr = process.communicate()
    print(stdout)
    if process.returncode != 0: 
        print('autoAnsible: ERROR attempting to create Ansible dir.')
        raise subprocess.CalledProcessError(process.returncode, 'su', stderr)
    
def mk_ansible_inventory(user:str):
    '''
    Create our "../ansible/hosts" inventory file under the fresh dir we created
    during install_ansible(). We will POPULATE this inventory and share SSH 
    keys for interactions in another function named 'stage_ansible_inventory()'
    '''
    print("autoAnsible: creating Ansible 'hosts' file in 'ansible' user-space.")
    su_command = 'touch $HOME/ansible/hosts'
    process = subprocess.Popen(['su', user, '-c', su_command], text=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    stdout, stderr = process.communicate()
    print(stdout)
    if process.returncode != 0: 
        print("autoAnsible: ERROR attempting to create Ansible 'hosts' file.")
        raise subprocess.CalledProcessError(process.returncode, 'su', stderr)  

def stage_ansible_inventory():
    '''
    Function converting user input into a formatted 'hosts' file to be used by
    ansible as its inventory.
    '''
    # We expect the 'hosts' file to reside under '/home/ansible/ansible/hosts'
    # as created by the install_ansible() func. 
    hostspath = '/home/ansible/ansible/hosts'
    print("autoAnsible: Staging the Ansible Inventory File, get your node " \
    "IP's ready...")
    if os.path.isfile(hostspath): 
        # Hosts file is present as expected. 
        # Check if Hosts path is already populated.
        if os.path.getsize(hostspath) != 0:
            print('autoAnsible: Hosts path is already populated with...\n')
            with open(hostspath) as f:
                print(f.read())
        else: 
            # If host file is empty, take user input to populate. 
            # We could be very fancy here with user input, but for the demo I
            # am simply converting the user provided string to a proper list. 
            # ...We should also be doing better input validation here...
            print("autoAnsible: [?] What is your Control-nodes hostname and" \
            " IP? (-> use ['hostname', 10.1.2.3] format, including brackets)...")
            master_list = list(input())
            print("autoAnsible: [?] What is your Worker-node(s) hostname and" \
            " IP(s)? (-> use ['host1', 10.1.2.3, 'host2', 10.1.2.4] format, including brackets)...")
            worker_list = list(input())
            print(master_list, worker_list)
    else: 
        print("autoAnsible: Hosts file is missing, generating it...")
        mk_ansible_inventory()


def gen_ansible_sshkeys(user:str):
    '''
    This should be ran by the 'ansible' user. We will generate our SSH keys
    for ansible interactions here. Keys will be named based on the hostname. 
    This is ran for both '--worker-node' and '--control-node' flows as these
    SSH keys will be used trust in place of passwords. 
    '''
    hostname = os.uname().nodename
    # For the sake of the demo, I am omitting the password declaration when
    # generating the keys (-N ""). For Production deployments, you should use
    # a passphrase for your certs to prevent tampering if they fall into the 
    # wrong persons hands. 
    print(f"autoAnsible: Generating SSH key named '{hostname}' for future Ansible Interactions")
    keygen_args = ['ssh-keygen', '-f', hostname, '-N', "", '-q']
    process = subprocess.Popen(['su', user, '-c', keygen_args], text=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    stdout, stderr = process.communicate()
    print(stdout)
    print(f"autoAnsible: SSH key named '{hostname}' succesfully created.")
    if process.returncode != 0: 
        print("autoAnsible: ERROR generating SSH key for Ansible")
        raise subprocess.CalledProcessError(process.returncode, 'su', stderr)  



def _control_node_install():
    '''
    --control-node' arg is called during install where we will configure our
    ansible user, pip3, and ansible-core control node.
    '''
    print('autoAnsible: Starting [control-node] installation!')
    create_user()
    update_pkg_manager()
    install_pip()
    # Note the 'ansible' user declared in the below functions. We expect these
    # functions to be ran in the context of the 'ansible' user, NOT root/sudo. 
    # This is critical so we are not deploying ansible-core package using the
    # root/sudo account for least-privilege or confusing file permissions.
    install_ansible('ansible')
    mk_ansible_inventory('ansible')
    stage_ansible_inventory('ansible')
    print('autoAnsible: [control-node] installation COMPLETE!')

def _worker_node_install():
    '''
    --worker-node' arg is called during install where we will configure our
    ansible user only.
    '''
    print('autoAnsible: Starting [worker-node] installation!')
    create_user()
    update_pkg_manager()
    print('autoAnsible: [worker-node] installation COMPLETE!')


if __name__ == '__main__':
    # Checking if script was called with sudo as required.
    if 'SUDO_USER' not in os.environ:
        print("ERROR: Please run this script using 'sudo', " \
        "ex.) 'sudo python3 autoAnsible --worker-node")
        sys.exit(1)
    else:
        # Checking if arguments were used. In this script we expect 3 options... 
        # 1: No args, meaning we should prompt the user if this is a worker or
        #   control node deployment. 
        # 2: '--control-node' where we will config  user, pip3, and ansible-core
        # 3: '--worker-node' where we will config user only. 
        if len(sys.argv) > 1: 
            arg = sys.argv[1]
            if arg == '--control-node': 
                _control_node_install()
            if arg == '--worker-node': 
                _worker_node_install()
        else: 
            print("ERROR: No argument provided. Please use either '--worker-node', " \
            "or '--control-node' when using this script.\n " \
            "ex.) sudo python3 autoAnsible.py --worker-node")
            sys.exit(1)


        
