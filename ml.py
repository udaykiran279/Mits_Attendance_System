import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
df=pd.read_csv("class-merge.csv")
x=df.drop("place",axis=1)
y=df.place
#x_train,x_test,y_train,y_test=train_test_split(features, labels, test_size=0.2, random_state=42)
knn = KNeighborsClassifier(n_neighbors=1,metric='manhattan')
knn.fit(x,y)
pickle.dump(knn,open("model.pkl","wb"))



