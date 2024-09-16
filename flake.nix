{
  description = "Persistent Python environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.05";
    flake-utils.url = "github:numtide/flake-utils";
    wkhtmltopdf-flake.url = "github:iledarn/WKHTMLTOPDFNIX";
  };

  outputs = { self, nixpkgs, flake-utils, wkhtmltopdf-flake }:
  flake-utils.lib.eachDefaultSystem (system:
  let
    pkgs = nixpkgs.legacyPackages.${system};

    odoorpc = pkgs.python310Packages.buildPythonPackage rec {
      pname = "OdooRPC";
      version = "0.10.1";
      format = "wheel";  # Specify that this is a wheel

      src = pkgs.fetchPypi {
        inherit pname version format;
        dist = "py2.py3";
        python = "py2.py3";
        sha256 = "a0900bdd5c989c414b1ef40dafccd9363f179312d9166d9486cf70c7c2f0dd44"; # Replace with actual hash
      };

      doCheck = false;  # Skip tests if they're causing issues
      propagatedBuildInputs = with pkgs.python310Packages; [
        # Add any dependencies OdooRPC needs here
      ];
    };

    pythonEnv = pkgs.python310.withPackages (ps: with ps; [
      odoorpc
      babel
      chardet
      cryptography
      decorator
      docutils
      ebaysdk
      freezegun
      gevent
      greenlet
      idna
      jinja2
      libsass
      lxml
      markupsafe
      num2words
      ofxparse
      passlib
      pillow
      polib
      psutil
      psycopg2
      pydot
      pyopenssl
      pypdf2
      pyserial
      python-dateutil
      python-ldap
      python-stdnum
      pytz
      pyusb
      qrcode
      reportlab
      requests
      urllib3
      vobject
      werkzeug
      xlrd
      xlsxwriter
      xlwt
      zeep
      beautifulsoup4
      cachetools

      setuptools
      mock
    ]);

    wkhtmltopdf = wkhtmltopdf-flake.packages.${system}.default;

    myEnv = pkgs.buildEnv {
      name = "my-python-env-3-10-13";
      paths = with pkgs; [
        pythonEnv
        sassc
        s3fs
        postgresql_15
        wkhtmltopdf
      ];
    };
  in
  {
    packages.default = myEnv;

    apps.default = {
      type = "app";
      program = "${myEnv}/bin/python";
    };
  }
  );
}
