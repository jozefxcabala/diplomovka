VYTVORENIE PROSTREDIA 
1. nainstaloval som MINICONDA
2. nainstaloval som ultralyticis (YOLO)
  - conda create --name ultralytics-env python=3.11 -y
  - aktivacia conda activate diploma-thesis-prototype
3. instalacia ultralytics - conda install -c conda-forge ultralytics
4. instalacia torch - conda install pytorch torchvision -c pytorch
5. vytvorenie prostredia - conda env export --name diploma-thesis-prototype > diploma-thesis-prototype-env.yml
6. 