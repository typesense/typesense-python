{
  description = "typesense-python development shell";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs =
    { self, nixpkgs }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "aarch64-darwin"
      ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
    in
    {
      devShells = forAllSystems (
        system:
        let
          pkgs = import nixpkgs { inherit system; };

          # Starts a local server configured like the one in CI, which the test suite expects.
          typesense-dev = pkgs.writeShellApplication {
            name = "typesense-dev";
            runtimeInputs = [ pkgs.typesense ];
            text = ''
              root="''${TYPESENSE_DEV_DIR:-$PWD/.typesense}"
              mkdir -p "$root/data" "$root/analytics"
              exec typesense-server \
                --api-key=xyz \
                --data-dir="$root/data" \
                --enable-search-analytics=true \
                --analytics-dir="$root/analytics" \
                --analytics-flush-interval=60 \
                --analytics-minute-rate-limit=50 \
                --enable-cors \
                "$@"
            '';
          };

          mkShell =
            python:
            pkgs.mkShell {
              packages = [
                python
                pkgs.uv
                pkgs.typesense
                typesense-dev
              ];

              env = {
                # Keep uv on the interpreter from this shell instead of fetching its own.
                UV_PYTHON = python.interpreter;
                UV_PYTHON_DOWNLOADS = "never";
              };

              shellHook = ''
                unset PYTHONPATH
              '';
            };
        in
        {
          default = mkShell pkgs.python313;
          py311 = mkShell pkgs.python311;
          py312 = mkShell pkgs.python312;
          py313 = mkShell pkgs.python313;
        }
      );
    };
}
