{
  pkgs ? import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/21.11.tar.gz") {}
} :
with pkgs;
let
  localhost-singularity = callPackage ./default.nix { python = python39; };
in
mkShell {
  buildInputs = [ glibcLocales localhost-singularity ];
  LOCALE_ARCHIVE_2_27 = "${glibcLocales}/lib/locale/locale-archive";
}
