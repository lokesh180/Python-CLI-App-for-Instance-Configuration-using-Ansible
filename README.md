# Python-CLI-App-for-Instance-Configuration-using-Ansible

This CLI Application accepts instance's name(s) as parameters and will configure given instances. The configuration is done by using
Ansible internally. The other part of the application will test the tasks.
This application will perform the below tasks:
1. Creating Temporary Directory on Instances->checking the directory created or not.
2. Uploading C Program File and Makefile(consists of command for compiling C Program) to Instances->Cheking both uploaded or not.
3. Executing C Program by using Makefile -> After Execution of makefile checking for executable exists or not.
4. Moving the C Executable file to current working directory-> checking executable file in current working directory.
5. Finally Deleting the Temporary Directory-> Cheking the directory deleted or not
