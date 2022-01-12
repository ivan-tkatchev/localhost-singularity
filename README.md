# localhost-singularity

A python program that will launch a shell with an isolated localhost network namespace.
(No internet access.)

Optionally one port can be proxied to the outside world.

A setup/teardown script can also be provided.

Depends on the Linux commands `ip`, `unshare` and `socat`.

A Nix derivation is provided to help you integrate this into your wider CI/CD infrastructure properly.

Run with `--help` to see the complete command line options.

*N.B.* The command provided to `--setup` will be launched *in the background* before launching the shell. After the shell finishes, a SIGTERM will be sent to the setup command, and the command will be waited to completion.

The intent is to provide services in the isolated shell, usually launched with some sort of process manager that doesn't daemonize. (I suggest `supervisord`.)

Example demonstration:

```
$ echo <<EOF > setup.sh
#!/bin/bash
nc -l 8080 > out.log
EOF
$ chmod +x setup.sh

$ localhost-singularity --setup ./setup.sh 
localhost-singularity:$ ip addr
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host 
       valid_lft forever preferred_lft forever
localhost-singularity:$ echo "Hello!" | nc -N localhost 8080
localhost-singularity:$ exit

$ cat out.log 
Hello!

$ 
```
