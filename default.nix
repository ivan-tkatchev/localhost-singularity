{ stdenv
, python
, util-linux
, socat
, iproute2
, fetchFromGitHub
, makeWrapper
, bashInteractive
} :
stdenv.mkDerivation {
  name = "localhost-singularity";
  src = ./.;
  buildInputs = [ makeWrapper ];
  buildPhase = "true";
  installPhase = ''
    mkdir -p $out/bin
    cp -f *.py $out
  '';
  fixupPhase = ''
    makeWrapper "${python.interpreter}" "$out/bin/localhost-singularity" \
      --add-flags "$out/localhost-singularity.py" \
      --add-flags "--sh ${bashInteractive}/bin/bash" \
      --add-flags "--ip ${iproute2}/bin/ip" \
      --add-flags "--unshare ${util-linux}/bin/unshare" \
      --add-flags "--socat ${socat}/bin/socat"
  '';
}
