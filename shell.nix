{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    # Python
    uv

    # library dependencies
    libxml2
    libxslt
    zlib
	cairosvg # https://cairosvg.org/
    
    # Build tools
    pkg-config
    gcc

	nodejs_20
	docker
	imagemagick
  ];
}
