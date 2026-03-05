{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    # Python
    uv

    # lxml dependencies
    libxml2
    libxslt
    zlib
    
    # Build tools
    pkg-config
    gcc

	nodejs_20
  ];
}
