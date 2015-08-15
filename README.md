# remoteaut
Executes Websphere MQ AUT scripts remotely using an MQ process on the queue manager to execute the AUT script.

Requires the AUT files to be accessaible by the queue manager for example:
- at work I use my roaming unix account that is accessible from all the MQ servers 
- AUT scripts are placed in a directory in my unix profile
- the scripts are chmod'ed to be executable
- I run 'remoteaut' from my desktop spcifying the path to the script /home/username/path/to/aut/directory/script.aut
~~~
remoteaut.exe -m <queue_manager> -c <channel> -i <hostname> -p <port> -f </file/path/to/aut.AUT>
~~~
You can use a bat file to execute it multiple times across multiple queue managers
