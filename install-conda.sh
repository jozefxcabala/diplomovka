#!/bin/bash

# 1. Stiahni Miniconda
echo "Stiahnutie Miniconda inštalátora..."
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh

# 2. Nainštaluj Miniconda
echo "Inštalácia Miniconda..."
bash ~/miniconda.sh -b -p $HOME/miniconda

# 3. Inicializácia Miniconda
echo "Inicializácia Miniconda..."
eval "$($HOME/miniconda/bin/conda shell.bash hook)"

# 4. Nastavenie cesty k Conda (pridá Miniconda do PATH)
echo "Nastavenie cesty k Conda..."
conda init

echo "Hotovo! Conda bola nainstalovana."
