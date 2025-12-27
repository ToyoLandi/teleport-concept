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
        # Create user without a home directory
        subprocess.run(['useradd', username], check=True)
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
        #if os.path.exists(f"/home/{username}"):
        #    subprocess.run(['userdel', '-r', username])
        #    print(f"autoAnsible: [*] Rolled back user creation for '{username}'.")
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

def install_pip(user:str):
    '''
    This should be ran using the 'ansible' user.

    Runs the `dnf install python3.12-pip -y` process on the host OS shell. 
    '''
    print("autoAnsible: Installing [pip] via dnf for 'ansible' user")
    su_command = 'dnf install python3.12-pip -y'
    process = subprocess.Popen(['su', user, '-c', su_command], text=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    stdout, stderr = process.communicate()
    print(stdout)
    if process.returncode != 0: 
        raise subprocess.CalledProcessError(process.returncode, 'dnf', stderr)

def install_ansible(user:str):
    '''
    This should be ran using the 'ansible' user.

    Runs the `pip3 install ansible-core --user` process on the host OS shell. 
    '''
    print("autoAnsible: Installing [ansible-core] via pip for 'ansible' user")
    su_command = 'python3 -m pip install --user ansible-core'
    process = subprocess.Popen(['su', user, '-c', su_command], text=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    stdout, stderr = process.communicate()
    print(stdout)
    if process.returncode != 0: 
        raise subprocess.CalledProcessError(process.returncode, 'dnf', stderr)

def _control_node_install():
    '''
    --control-node' arg is called during install where we will configure our
    ansible user, pip3, and ansible-core control node.
    '''
    print('autoAnsible: Starting [control-node] installation!')
    create_user()
    update_pkg_manager()
    install_pip()
    install_ansible()
    print('autoAnsible: [control-node] installation COMPLETE!')

def _worker_node_install():
    '''
    --worker-node' arg is called during install where we will configure our
    ansible user only.
    '''
    print('autoAnsible: Starting [worker-node] installation!')
    create_user()
    update_pkg_manager()


if __name__ == '__main__':
    # Checking if script was called with sudo as required.
    if 'SUDO_USER' not in os.environ:
        print("ERROR: Please run this script using 'sudo', " \
        "ex.) 'sudo python3 autoAnsible --worker-node")
        sys.exit(1)
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


        
