from PIL import Image as PIL_Image
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision.transforms as transforms
import torchvision.models as models
from fastai.vision import load_learner, Image

# import os
# 
# cwd = os.getcwd()  # Get the current working directory (cwd)
# files = os.listdir(cwd)  # Get all the files in that directory
# print("Files in '%s': %s" % (cwd, files))

# В данном классе мы хотим полностью производить всю обработку картинок, которые поступают к нам из телеграма.
class ClassPredictor:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")        
        self.model = load_learner("../model/shrooms")
        self.to_tensor = transforms.ToTensor()

    def predict(self, img_stream):        
        # получим предсказания по картинке
        pred, _, probs = self.model.predict(self.process_image(img_stream))
        prob = int(probs.max() * 100)  # получаем вероятность предсказанного класса в %

        return pred, prob
    
    def process_image(self, img_stream):
        # используем PIL, чтобы получить картинку из потока и изменить размер
        image = PIL_Image.open(img_stream).resize((256, 256))
        # переводим картинку в тензор и оборачиваем в объект Image, который использует fastai у себя внутри
        image = Image(self.to_tensor(image))
        return image
