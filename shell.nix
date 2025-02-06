# pygame setup for nix-shell

{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
    buildInputs = [
        pkgs.python3
        pkgs.python3Packages.pygame
    ];
}