{ pkgs ? import <nixpkgs> {} }:

let
  # Create an environment with all necessary libraries
  libEnv = pkgs.buildEnv {
    name = "invenio-libs";
    paths = with pkgs; [
      cairo
      pango
      gdk-pixbuf
      glib
      libxml2
      libxslt
      zlib
    ];
  };
in

pkgs.mkShell {
  buildInputs = with pkgs; [
    # Python
    uv

    # Build tools
    pkg-config
    gcc

    nodejs_20
    docker
    imagemagick
  ];

  nativeBuildInputs = [ libEnv ];

  shellHook = ''
    export UV_SYSTEM_PYTHON=0
    unset PYTHONPATH
    
    export LD_LIBRARY_PATH="${libEnv}/lib:$LD_LIBRARY_PATH"
    export PKG_CONFIG_PATH="${libEnv}/lib/pkgconfig:$PKG_CONFIG_PATH"
    export DYLD_LIBRARY_PATH="${libEnv}/lib:$DYLD_LIBRARY_PATH"
  '';
}

