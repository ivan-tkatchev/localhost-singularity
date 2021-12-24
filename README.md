# localhost-singularity

A python program that will launch a shell with an isolated localhost network namespace.
(No internet access.)

Optionally one port can be proxied to the outside world.

A setup/teardown script can also be provided.

Depends on the Linux commands `ip`, `unshare` and `socat`.

A Nix derivation is provided to help you integrate this into your wider CI/CD infrastructure properly.

Run with `--help` to see the complete command line options.
