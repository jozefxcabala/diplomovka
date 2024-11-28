# Postup
1. conda create --name ultralytics-env python=3.8 -y
2. conda activate ultralytics-env
3. conda install -c pytorch -c nvidia -c conda-forge pytorch torchvision pytorch-cuda=11.8 ultralytics -y
4. pip install super-gradients
5. Skus spustit helloWorld.py
6. vyexportuj si env ---  conda env export > environment.yml

# helloWorld.py
```from ultralytics import NAS

# Load a COCO-pretrained YOLO-NAS-s model
model = NAS("yolo_nas_s.pt")

# Display model information (optional)
model.info()

# Validate the model on the COCO8 example dataset
results = model.val(data="coco8.yaml")

# Run inference with the YOLO-NAS-s model on the 'bus.jpg' image
results = model("data/bus.jpg")
```


