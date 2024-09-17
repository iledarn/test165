.. code-block:: bash

   git clone https://github.com/iledarn/test165.git
   cd test165
   nix profile install

   gitaggregate -c repos.yaml

   python autoaggregate.py

   gitaggregate -c auto_repos.yaml

   cd ~

   git clone <your_private_doodba_based_repo>

   ln -s /home/ubuntu/<private_doodba_repo_name>/odoo/custom/src/private/ test165/

   cd test165

   mkdir -p auto/addons

   python 40-addons-link.py
