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
    This should be ran as our 'sudo' user.

    Creates an explict 'ansible' user to be used for Ansible interactions such
    as running playbooks.
    '''
    print("autoAnsible: Creating explict 'ansible' user")
    # We could accept user input here for a username besides 'ansible' but for
    # the sake of the demo, lets keep this username explict. 
    username = 'ansible'

    # Check if user already exist on the node.
    try:
        subprocess.run(['id', username], 
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"autoAnsible: User '{username}' already exists.")
        return
    except subprocess.CalledProcessError:
        # User does not exist, proceed with creation
        pass
    # Prompt for 'ansible' password
    print("autoAnsible: -> IMPORTANT - Be sure the password you're about to " \
    "type matches on all 3 nodes <--")
    password = getpass.getpass("autoAnsible: Enter password for 'ansible' user: ").strip()
    
    try:
        print(f"autoAnsible: Creating user '{username}'...")
        # Create user with a home directory
        subprocess.run(['useradd', username, '-m'], check=True)
        # Set the password using chpasswd (more secure)
        # chpasswd expects input in the format "username:password"
        process = subprocess.Popen(['chpasswd'], 
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate(input=f"{username}:{password}")
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, 'chpasswd', stderr)
        print(f"autoAnsible: User '{username}' created successfully.")

    except subprocess.CalledProcessError as e:
        print(f"autoAnsible: ERROR Failed to create user: {e.stderr if hasattr(e, 'stderr') else e}")
        # TODO - Handle cleanup without checking home dir, as home dir is not being created
        # Clean up if useradd succeeded but chpasswd failed
        if os.path.exists(f"/home/{username}"):
            subprocess.run(['userdel', '-r', username])
            print(f"autoAnsible: Rolled back user creation for '{username}'.")
        sys.exit(1)

def update_pkg_manager():
    '''
    This should be ran as our our 'sudo' user.

    Runs the `dnf update -y` process on the host OS shell. 
    '''
    print('autoAnsible: Updating package manager repo')
    # TODO - check host os package manager in use (dnf, yum, apt-get) & update
    process = subprocess.Popen(['dnf', 'update', '-y'], 
                               text=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    stdout, stderr = process.communicate()
    #print(stdout)
    if process.returncode != 0: 
        raise subprocess.CalledProcessError(process.returncode, 'dnf', stderr)

def install_pip():
    '''
    This should be ran using the 'sudo' user.

    Runs the `dnf install python3.12-pip -y` process on the host OS shell. 
    '''
    print("autoAnsible: Installing [pip] via dnf")
    pkg = 'python3.12-pip'
    process = subprocess.Popen(['dnf', 'install', pkg, '-y'], 
                               text=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    stdout, stderr = process.communicate()
    #print(stdout)
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
    print("autoAnsible: Installing [ansible-core] via pip for 'ansible' user.")
    su_command = 'python3 -m pip install --user ansible-core'
    process = subprocess.Popen(['su', user, '-c', su_command], text=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    stdout, stderr = process.communicate()
    #print(stdout)
    if process.returncode != 0: 
        print('autoAnsible: ERROR during ansible-core installation.')
        raise subprocess.CalledProcessError(process.returncode, 'su', stderr)
    
    # Additionally, we need to create the '/home/ansible/ansible' directory since we
    # used pip to install with our ansible user, we were unable to write to the
    # default location of "/etc/ansible". 
    print("autoAnsible: Creating '~/ansible' directory for 'ansible' user.")
    # Checking if ansible dir already exist from a previous run for example...
    dirpath = '/home/ansible/ansible'
    if os.path.exists(dirpath):
        print("autoAnsible: '~/ansible' directory already exist!")
        return
    else:
        # otherwise, create our ansible dir. 
        su_command = f"mkdir {dirpath}"
        process = subprocess.Popen(['su', user, '-c', su_command], text=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        stdout, stderr = process.communicate()
        print(stdout)
        if process.returncode != 0: 
            print('autoAnsible: ERROR attempting to create Ansible dir.')
            raise subprocess.CalledProcessError(process.returncode, 'su', stderr)

def install_ansible_x509(user:str):
    '''
    This should be ran with our 'ansible' user

    Since we are using ansible-core, we need to install the
    community.crypto.x509 manually via ansible-galaxy. 
    '''
    print("autoAnsible: Attempting to install community.crypto.x509 for Ansible")
    su_command = ("ansible-galaxy collection install community.crypto")
    process = subprocess.Popen(['su', user, '-c', su_command], 
                               text=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0: 
        print("autoAnsible: ERROR attempting to install community.crypto.x509 for Ansible")
        raise subprocess.CalledProcessError(process.returncode, 'su', stderr)
    else:
        print("autoAnsible: Successfully installed community.crypto.x509 for Ansible")

def pull_ansible_inventory(user:str):
    '''
    This should be ran by our 'ansible' user. 

    Create our "../ansible/hosts" inventory file under the fresh dir we created
    during install_ansible(). This will pull the sample from demo repo. 
    
    MAKE SURE YOU MODIFY THIS FILE WITH YOUR HOSTNAMES AND IPs! 
    '''
    print("autoAnsible: Fetching sample Ansible '.../ansible/hosts.yaml'")
    hosts_repourl = 'https://raw.githubusercontent.com/ToyoLandi/teleport-concept/refs/heads/main/ansible/hosts.yaml'
    su_command = (f"curl {hosts_repourl} -o $HOME/ansible/hosts.yaml -s -m 8")
    process = subprocess.Popen(['su', user, '-c', su_command], 
                               text=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0: 
        print("autoAnsible: ERROR while fetching Sample Ansible 'hosts' file.")
        raise subprocess.CalledProcessError(process.returncode, 'su', stderr)  

def gen_ansible_sshkeys(user:str):
    '''
    This should be ran by the 'ansible' user. We will generate our SSH keys
    for ansible interactions here. Keys will be named based on the hostname. 
    This is ran for both '--worker-node' and '--control-node' flows as these
    SSH keys will be used trust in place of passwords. 
    '''
    keyname = (os.uname().nodename) + '_rsa'
    keypath = f'/home/{user}/.ssh/{keyname}'
    # For the sake of the demo, I am omitting the password declaration when
    # generating the keys (-N ""). For Production deployments, you should use
    # a passphrase for your certs to prevent tampering if they fall into the 
    # wrong persons hands. 
    if os.path.exists(keypath):
        print(f"autoAnsible: SSH key '{keyname}' already exist - skipping this step.")
        return
    print(f"autoAnsible: Generating SSH key named '{keyname}' to '{keypath}'")
    su_command = f'ssh-keygen -f {keypath} -N "" -q'
    process = subprocess.Popen(['su', user, '-c', su_command], text=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    stdout, stderr = process.communicate()
    #print(stdout)
    if process.returncode != 0: 
        print("autoAnsible: ERROR generating SSH key for Ansible")
        raise subprocess.CalledProcessError(process.returncode, 'su', stderr)
    else:
        print(f"autoAnsible: SSH key named '{keyname}' succesfully created.")

def gen_ssh_copy_commands(user:str):
    '''
    This function takes the generated SSH keys from gen_ansible_sshkeys and
    copies them to our other nodes for Ansible future interactions. 
    '''
    keyname = (os.uname().nodename) + '_rsa'
    keypath = f'~/.ssh/{keyname}' + '.pub' #As we are only copying the pubkey.
    command_list = []
    # Take user input on the neighboring nodes where the pubkey should be sent.
    # TODO, we could pass these values back to the hosts.yaml file to save,
    #   steps, but this makes reduces host.yaml extensibility for future 
    #   deployments.
    # TODO -- subprocess doesnt like interactable commands like 
    #   `ssh-copy-id` as it asks to check fingerprint, and request the
    #   remote-host users password to auth adding the keys + ssh likes user 
    #    context (not su) instead of reinventing the wheel, it may be better
    #    to just use the term. For the demo lets simply paste the preformatted
    #    command you should run outside of the script as the 'ansible' user.
    print('autoAnsible: Please provide the node IPs we will share our pubkey - this will print a command template\n' \
    '                   [ syntax ?> 10.99.0.10,10.99.0.11,10.99.0.12 ]')
    iplist = list(input('?> ').split(","))
    if len(iplist) >= 1:
        for ip in iplist:
            command_template = f'ssh-copy-id -i {keypath} {user}@{ip}'
            command_list.append(command_template)
        print("autoAnsible: Successfully generated [ssh-copy-id] commands")
        return command_list
    else: 
        print("autoAnsible: No node IPs for [ssh-copy-id] commands were provided.")

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
    pull_ansible_inventory('ansible')
    gen_ansible_sshkeys('ansible')
    command_list = gen_ssh_copy_commands('ansible')
    print("autoAnsible: [control-node] staging complete! \n\n" \
    "    |=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=|\n" \
    "    |   1. Be sure to modify the 'ansible' users '~/ansible/hosts.yaml'     |\n" \
    "    |     file with your specific Hostnames, IPs, etc before running        |\n" \
    "    |     any Ansible commands.                                             |\n" \
    "    |   2. To allow for Ansible Connections, Be sure to run the following   |\n" \
    "    |     commands from the 'ansible' users terminal to distribute the      |\n" \
    "    |     generated SSH Keys *AFTER* all nodes have been staged.            |\n" \
    "    |=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=|\n" )
    print('su ansible')
    for cmd in command_list:
        print(cmd)
    print("\n")
    return

def _worker_node_install():
    '''
    --worker-node' arg is called during install where we will configure our
    ansible user only.
    '''
    print('autoAnsible: Starting [worker-node] installation!')
    create_user()
    update_pkg_manager()
    #gen_ansible_sshkeys('ansible')
    #command_list = distribute_keys('ansible')
    print("autoAnsible: [worker-node] staging complete!")
    

if __name__ == '__main__':
    # Checking if script was called with sudo as required.
    if 'SUDO_USER' not in os.environ:
        print("autoAnsible: ERROR Please run this script using 'sudo', " \
        "ex.) 'sudo python3 autoAnsible --worker-node")
        sys.exit(1)
    else:
        # Checking if arguments were used. In this script we expect 2 options... 
        # 2: '--control-node' where we will config user, pip3, and ansible-core
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