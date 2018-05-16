#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import SmartViewerUI  # import du fichier SmartViewerUI.py généré par pyuic5

import sys
import os

#BDD
import sqlite3
from SmartViewerDatabase import *

from keras.applications.resnet50 import ResNet50
from keras.preprocessing import image
from keras.applications.resnet50 import preprocess_input, decode_predictions
from keras.models import Model

import numpy as np

model = ResNet50(weights='imagenet')
model2 = Model(inputs=model.input, outputs=[model.output, model.get_layer('flatten_1').output])

#VARIABLES
ImageExtensions = ('.png', '.PNG', '.jpeg', '.JPEG', 'jpg', 'JPG')
MAX_COLUMN = 4
DatabaseName = 'SmartViewer.db'

#BDD
BDD = sqlite3.connect(DatabaseName)
QueryCurs = BDD.cursor()
CreateTable(QueryCurs)

#Image
class ImageViewer(QMainWindow):

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.ui = SmartViewerUI.Ui_SmartViewer()
        self.ui.setupUi(self) 
        self.imagesList = []     
        # events
        self.connectActions()
   
    def connectActions(self):
        self.ui.actionQuit.triggered.connect(qApp.quit)
        self.ui.btn_openDirectory.clicked.connect(self.openDirectoryDialog)
        self.ui.btn_search.clicked.connect(self.search)
        self.ui.btn_apply.clicked.connect(self.apply)

    def openDirectoryDialog(self):
        print("openDirectoryDialog button event")
        filename = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if filename:
            self.ui.tb_directoryPath.setText(filename)

    def search(self):
        print("Search button event")
        try:
            self.imagesList.clear()
            path = self.ui.tb_directoryPath.text()
            if self.ui.cb_subdirectory.isChecked():
                for root, dirs, files in os.walk(path):
                   for filename in files:
                    if filename.endswith(ImageExtensions):
                        imgPath = os.path.join(root, filename)
                        self.imagesList.append(imgPath)
            else:
                for filename in os.listdir(path):
                    if filename.endswith(ImageExtensions):
                        imgPath = os.path.join(path, filename)
                        self.imagesList.append(imgPath)
            self.displayImages(self.imagesList)
            self.tagImages(self.imagesList)
        except OSError as e:
            QMessageBox.critical(self, "Error", "Path not defined or incorrect : Select a directory")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def displayImages(self, imagesList):
        #delete
        while self.ui.gridLayoutImages.count():
            item = self.ui.gridLayoutImages.takeAt(0)
            widget = item.widget()
            widget.deleteLater()

        row, col = 0, 0
        for image in imagesList:
                if col == MAX_COLUMN:
                    row += 1
                    col = 0
                label = QLabel()
                pixmap = QPixmap(image)
                pixmap = pixmap.scaledToWidth(100)
                label.setPixmap(pixmap)
                self.ui.gridLayoutImages.addWidget(label,row,col)
                col +=1
        self.ui.lb_nbImages.setText(str(len(imagesList))+" Images")
        print("Update done")
    
    def tagImages(self, imagesList):
        for img_path in imagesList: 
            if not ImageExist(QueryCurs, img_path): 
                print("tag image : " + img_path+ "\n")    
                img = image.load_img(img_path, target_size=(224, 224))
                x = image.img_to_array(img)
                x = np.expand_dims(x, axis=0)
                x = preprocess_input(x)
                # prédiction et résultat
                preds, sign = model2.predict(x)
                sign = sign[0,:]
                print(type(sign), sign.shape, sign)
                tags = decode_predictions(preds, top=5)[0]
                AddEntry(QueryCurs,img_path, tags[0][1], tags[1][1], tags[2][1], tags[3][1], tags[4][1]) 
        BDD.commit()
        print("tagImages done") 
    
    def apply(self):
        print("Apply button event")	
        keywords = self.ui.tb_keywords.text().split(" ")
        print(keywords)
        if not keywords:
            self.display(self.imagesList)
            return		
        print("Keywords are:")
        imagesListWithFilter = []
        for keyword in keywords:
            print(keyword)
            imagesListWithFilter += GetImageWithFilter(QueryCurs, keyword)
        imagesListWithFilter = [i for i in imagesListWithFilter if i in self.imagesList]
        self.displayImages(imagesListWithFilter)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = ImageViewer()
    window.show()
    sys.exit(app.exec_())
