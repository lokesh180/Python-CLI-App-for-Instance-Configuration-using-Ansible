#!/usr/bin/env python3
"""
This CLI Application accepts instance's name(s) as parameters and will configure given instances. The configuration is done by using
Ansible internally. The other part of the application will test the tasks.
This application will perform the below tasks:
1. Creating Temporary Directory on Instances->checking the directory created or not.
2. Uploading C Program File and Makefile(consists of command for compiling C Program) to Instances->Cheking both uploaded or not.
3. Executing C Program by using Makefile -> After Execution of makefile checking for executable exists or not.
4. Moving the C Executable file to current working directory-> checking executable file in current working directory.
5. Finally Deleting the Temporary Directory-> Cheking the directory deleted or not
"""

#Importing Required Modules
import sys,os
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_bytes, to_native
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.module_utils.common.collections import ImmutableDict
from ansible import context
from ansible.plugins.callback import CallbackBase

#Creating a list for given Instance names
hosts_list=[]

def main():
    # Checking the length of parameters
    n = len(sys.argv)
    # Checking whether parameters given were atleast 2(including file name $0)
    if n < 2:
        print("Usage : "+sys.argv[0]+" Instance(s)")
        sys.exit(1)
    # Storing arguments to list
    for i in range(1,n):
        hosts_list.append(sys.argv[i])

    # Providing command line arguments to ansible context as a Immutable Dictionary.
    context.CLIARGS = ImmutableDict(connection='smart', module_path=['/etc'], forks=10, become=None,
                                    become_method=None, become_user=None, check=False, diff=False, verbosity=0)
    #Adding given Insatnce names with camma(,) in single string.
    sources = ','.join(hosts_list)
    if len(hosts_list) == 1:
        sources += ','
    # Creating Objects to DataLoader, InventoryManager, VaraibleManager.
    loader = DataLoader()
    loader_test= DataLoader()
    passwords = dict(vault_pass='secret')
    inventory = InventoryManager(loader=loader, sources=sources)
    variable_manager = VariableManager(loader=loader, inventory=inventory)
    inventory_test = InventoryManager(loader=loader_test, sources=sources)
    variable_manager_test = VariableManager(loader=loader_test, inventory=inventory_test)
    # Creating an object for TaskQueueManager by giving parameters, which constructor expects.
    tqm = TaskQueueManager(
        inventory=inventory,
        variable_manager=variable_manager,
        loader=loader,
        passwords=passwords,
    )
    # Creating a Playbook with Tasks and stores as Dictionary
    play_book = dict(
        name="Compiles and Install a C Program File on Remote Instances", # Name of the Play_Book
        hosts=hosts_list, # Setting Hosts list to hosts(similar to "all")
        gather_facts='yes', # Gathering all the tasks
        tasks=[
            #dict(action=dict(module='debug', args=dict(msg="Creating Temporary directory on Remote Instances"))),
            dict(action=dict(module='shell', args='mkdir Remote_Instance_dir')), #Creating Temporary Directory on Instances
            #dict(action=dict(module='debug', args=dict(msg="Uploading C Program File"))),
            dict(action=dict(module='copy', args=dict(src= 'matinv.c',dest='Remote_Instance_dir/'))), #Uploading C Program File to Instances
            #dict(action=dict(module='debug', args=dict(msg="Uploading Makefile(which has command for compilation)"))),
            dict(action=dict(module='copy', args=dict(src= 'Makefile',dest='Remote_Instance_dir/'))), #Uploading Makefile to Instances
            #dict(action=dict(module='debug', args=dict(msg="Running Makefile (Compiling C Program)"))),
            dict(action=dict(module='shell', args='make -C Remote_Instance_dir')), #Executing Makefile
            #dict(action=dict(module='debug', args=dict(msg="Installing C Executable File"))),
            dict(action=dict(module='copy', args=dict(remote_src=True, src= 'Remote_Instance_dir/mat_inv',dest='.'))), #Moving Executable to ouside of temporary Directory.
            #dict(action=dict(module='debug', args=dict(msg="Deleting Temporary directory"))),
            dict(action=dict(module='shell', args='rm -r Remote_Instance_dir')), #Deleting the Temporary Directory
            #dict(action=dict(module='debug', args=dict(msg="Giving Execute Permission"))),
            dict(action=dict(module='shell', args='chmod u+x mat_inv')), #Giving Execute Permission for Executable.
            #dict(action=dict(module='debug', args=dict(msg="Executing C Program"))),
            dict(action=dict(module='shell', args='./mat_inv -n 1024 -I fast -P 1 > output.txt')), #Executing Executable and storing output to a file on Instances
            #dict(action=dict(module='debug', args=dict(msg="SUCCESS"))),
        ]
    )

    # Creating an Object for Play and loading with playbook, loader and variable manager.
    play = Play().load(play_book, variable_manager=variable_manager, loader=loader)

   #Exception Handling
    try:
        # Running PlayBook(loaded play object) with TaskQueueManager
        result = tqm.run(play) 
    finally:
        # Cleaning all the forked processes and temparory files.
        tqm.cleanup()
        if loader:
            loader.cleanup_all_tmp_files()
    if result==0:
        print("----CONFIGURATION SUCCESS----")
    else:
        print("----CONFIGURATION FAILED----")

    tqm_test = TaskQueueManager(
        inventory=inventory_test,
        variable_manager=variable_manager_test,
        loader=loader_test,
        passwords=passwords,
    )
    # Creating a Playbook with Test cases and stores as Dictionary
    play_book_test = dict(
        name="Test Cases", # Name of the Play_Book
        hosts=hosts_list, # Setting Hosts list to hosts(similar to "all")
        gather_facts='no', 
        tasks=[
            
            dict(action=dict(module='shell', args='mkdir Remote_Instance_dir')), #Creating Temporary Directory on Instances
            dict(action=dict(module='shell', args='ls | grep Remote_Instance_dir'), register='shell_out'), # searching for directory
            dict(action=dict(module='assert', that="'Remote_Instance_dir' in shell_out.stdout")), #checking with shell_output
            
            dict(action=dict(module='copy', args=dict(src= 'matinv.c',dest='Remote_Instance_dir/'))), #Uploading C Program File to Instances
            dict(action=dict(module='shell', args='ls Remote_Instance_dir/ | grep matinv.c'), register='shell_out'), # searching for matinv.c
            dict(action=dict(module='assert', that="'matinv' in shell_out.stdout")), #checking with shell_output

            dict(action=dict(module='copy', args=dict(src= 'Makefile',dest='Remote_Instance_dir/'))), #Uploading Makefile to Instances
            dict(action=dict(module='shell', args='ls Remote_Instance_dir/ | grep Makefile'), register='shell_out'), # searching for Makefile
            dict(action=dict(module='assert', that="'Makefile' in shell_out.stdout")), #checking with shell_output
           
            dict(action=dict(module='shell', args='make -C Remote_Instance_dir')), #Executing Makefile
            dict(action=dict(module='shell', args='ls Remote_Instance_dir/ | grep mat_inv'), register='shell_out'), # searching for mat_inv in temparory directory
            dict(action=dict(module='assert', that="'mat_inv' in shell_out.stdout")), #checking with shell_output
            
            dict(action=dict(module='copy', args=dict(remote_src=True, src= 'Remote_Instance_dir/mat_inv',dest='.'))), #Moving Executable to ouside of temporary Directory.
            dict(action=dict(module='shell', args='ls | grep mat_inv'), register='shell_out'), # searching for mat_inv in current working directory
            dict(action=dict(module='assert', that="'mat_inv' in shell_out.stdout")), #checking with shell_output

            dict(action=dict(module='shell', args='rm -r Remote_Instance_dir')), #Deleting the Temporary Directory
            dict(action=dict(module='shell', args='ls'), register='shell_out'), # list of file and directories in current working directory.
            dict(action=dict(module='assert', that="'Remote_Instance_dir' not in shell_out.stdout")), #checking with shell_output
            
            dict(action=dict(module='shell', args='chmod u+x mat_inv')), #Giving Execute Permission for Executable.
            dict(action=dict(module='shell', args='stat -c "%a" mat_inv'), register='shell_out'), # getting permissions of mat_inv file.
            dict(action=dict(module='assert', that="'764' in shell_out.stdout")), #checking with shell_output
            
            dict(action=dict(module='shell', args='./mat_inv -n 1024 -I fast -P 1 > output.txt')), #Executing Executable and storing output to a file on Instances
            dict(action=dict(module='shell', args='ls | grep output.txt'), register='shell_out'), # searching for output.txt
            dict(action=dict(module='assert', that="'output.txt' in shell_out.stdout")), #checking with shell_output
        ]
    )

    # Creating an Object for Play and loading with playbook, loader and variable manager.
    play_test = Play().load(play_book_test, variable_manager=variable_manager_test, loader=loader_test)

   #Exception Handling
    try:
        # Running PlayBook(loaded play object) with TaskQueueManager
        result_test = tqm_test.run(play_test) 
    finally:
        # Cleaning all the forked processes and temparory files.
        tqm_test.cleanup()
        if loader_test:
            loader_test.cleanup_all_tmp_files()
    if result_test==0:
        print("-----ALL TEST CASES PASSED-----")
    else:
        print("-----ONE or MORE TEST CASES FAILED-----")

if __name__ == "__main__":
    main()