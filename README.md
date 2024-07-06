[![Support me on ko-fi](https://pabanks.io/assets/kofi-md.svg)](https://ko-fi.com/H2H1ZZY1Q) &nbsp; [![Support me on Coindrop](https://pabanks.io/assets/coindrop-md.svg)](https://coindrop.to/auxcodes)

# Remote AUT Scripts
Executes Websphere MQ AUT scripts remotely using an MQ process on the queue manager to execute the AUT script.

Requires the AUT files to be accessaible by the queue manager for example:
- at work I use my roaming unix account that is accessible from all the MQ servers 
- AUT scripts are placed in a directory in my unix profile
- the scripts are chmod'ed to be executable
- I run 'remoteaut' from my Windows desktop specifying the path to the script /home/username/path/to/aut/directory/script.aut
~~~
remoteaut.exe -m <queue_manager> -c <channel> -i <hostname> -p <port> -f </file/path/to/aut.AUT>
~~~
You can use a bat file to execute it multiple times across multiple queue managers.
