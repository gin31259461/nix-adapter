{
  description = "Cross-platform native reconciliation adapter for Nix deployments";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
  };

  outputs =
    { self, nixpkgs }:
    let
      supportedSystems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
    in
    {
      packages = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          nix-adapter = pkgs.python3Packages.buildPythonPackage {
            pname = "nix-adapter";
            version = "0.2.0";
            src = ./.;
            format = "pyproject";
            nativeBuildInputs = [ pkgs.python3Packages.flit-core ];
            propagatedBuildInputs = [
              pkgs.python3Packages.rich
              pkgs.python3Packages.tomli-w
            ];
            checkPhase = ''
              python -m unittest discover -s tests
            '';
          };
          adapterPython = pkgs.python3.withPackages (ps: [ nix-adapter ]);
        in
        {
          inherit nix-adapter adapterPython;
          default = nix-adapter;
        }
      );

      checks = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in
        {
          package = self.packages.${system}.default;
        }
      );

      devShells = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in
        {
          default = pkgs.mkShell {
            packages = [
              self.packages.${system}.adapterPython
              pkgs.python3Packages.flit-core
            ];
          };
        }
      );
    };
}
