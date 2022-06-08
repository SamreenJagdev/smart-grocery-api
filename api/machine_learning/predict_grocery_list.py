
import pandas as pd
import numpy as np
from sklearn import preprocessing
import pickle

#import JSON document
dfDate = pd.read_json (r'C:\Users\desan\OneDrive\Desktop\Courses\Senior Engineering Project\Final Project - Machine Learning\date.json')
dfItems = pd.read_json (r'C:\Users\desan\OneDrive\Desktop\Courses\Senior Engineering Project\Final Project - Machine Learning\items.json')

date = dfDate.to_numpy()
items = dfItems.to_numpy()

#format model input
itemList = np.unique(items[:,[3]])

dataSet = np.empty((len(itemList),4),dtype=object)

dateStr = str(date[0,0])

month = int(dateStr[5:7])
week = int(((int(dateStr[8:10]) - 1) / 7) +1)


for i in range(len(itemList)):
     dataSet[i,0] = itemList[i]
     dataSet[i,1] = month
     dataSet[i,2] = week

le = preprocessing.LabelEncoder()
le.fit(dataSet[:,0])
encoded_values = (le.transform(dataSet[:,[0]]))

#create class labels ad encode items
for j in range(len(itemList)):      
     dataSet[j,3] = encoded_values[j]

# load the model from disk
filename = 'smart_grocery_model.sav'
X = dataSet[:,[1,2,3]]
loaded_model = pickle.load(open(filename, 'rb'))
result = loaded_model.predict(X)
print(result)

result = result.reshape(len(result),1)
output = np.append(X,result,axis=1)

decoded_values = le.inverse_transform(X[:,[2]].astype(int)).reshape(len(X),1)

output = np.append(output,decoded_values,axis=1)

filtered_output = []

for k in range(len(output)): 
    if output[k,3] == 1:
        filtered_output.append(output[k,4])
       

df=pd.DataFrame(filtered_output, columns=["item"])

df.to_json(r'C:\Users\desan\OneDrive\Desktop\Courses\Senior Engineering Project\Final Project - Machine Learning\prediction.json',orient='records')

#print(filtered_output)


