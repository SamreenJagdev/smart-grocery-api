
import pandas as pd
import numpy as np
import datetime
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn import tree
from sklearn import metrics
from sklearn import tree
from matplotlib import pyplot as plt
import pickle
from sklearn import preprocessing

#import JSON document
df = pd.read_json (r'C:\Users\desan\OneDrive\Desktop\Courses\Senior Engineering Project\Final Project - Machine Learning\items.json')
df = df[["creation_timestamp", "item_name"]]
df['Month'] = np.NaN
df['Week'] = np.NaN

#create numpy array of all items
items = df.to_numpy()

#Prepare data
for i in range(len(items)):
     items[i,2] = int((datetime.datetime.strptime(items[i,0], '%Y-%m-%d %H:%M:%S.%f').date()).strftime("%m"))
     items[i,3] = int(((int((datetime.datetime.strptime(items[i,0], '%Y-%m-%d %H:%M:%S.%f').date()).strftime("%d"))-1) / 7)+1)

#create labelled data    
itemList = np.unique(items[:,[1]])
monthList = np.unique(items[:,[2]])
weekList = np.unique(items[:,[3]])

#compute dataSet dimensions
records = len(itemList) * len(monthList) * len(weekList)
dataSet = np.empty((records,5),dtype=object)

print(records)
print(itemList)
print(monthList)
print(weekList)
print(len(itemList))
print(len(monthList))
print(len(weekList))

#populate item column
index=0
counter = 0
for i in range(records):
     counter = counter + 1
     if counter > (records / len(itemList)):
          counter = 1
          index = index + 1
     dataSet[i,0] = itemList[index]

#create populate month column
index=0
counter = 0

for j in range(records):
     
     counter = counter + 1
     if counter > (records / len(itemList)) /len(monthList):
          counter = 1
          if index == (len(monthList) - 1):
               index = 0
          else:
               index = index + 1 
         
     dataSet[j,1] = monthList[index]
 

#create populate week column 
index=0
counter = 0
for k in range(records):

     counter = counter + 1
     if counter > len(weekList):
               index = 0
               counter = 1
     dataSet[k,2] = weekList[index]
     index = index + 1
     
le = preprocessing.LabelEncoder()
le.fit(dataSet[:,0])
encoded_values = (le.transform(dataSet[:,[0]]))

#create class labels ad encode items
for l in range(records):
    label = 0
    key1  = str(dataSet[l,0]) + "-"  + str(dataSet[l,1]) + "-" + str(dataSet[l,2])
    for m in range(len(items)):
     key2  = str(items[m,1]) + "-" + str(items[m,2]) + "-" + str(items[m,3]) 

     if (key1==key2):
          label=1
     dataSet[l,3] = label        
     dataSet[l,4] = encoded_values[l]

print(dataSet)
#create decision tree
X = dataSet[:,[1,2,4]]
y = dataSet[:,[3]]
y = y.astype('int') 


#create training and test data
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=0)

#train classifier
clf = DecisionTreeClassifier(criterion='gini',max_leaf_nodes=10, random_state=0,class_weight='balanced')
clf.fit(X, y)


#test classifier
y_pred = clf.predict(X_test)
print("Accuracy:",metrics.accuracy_score(y_test, y_pred))

#save the model to disk
filename = 'smart_grocery_model.sav'
pickle.dump(clf, open(filename, 'wb'))

#plot decision tree
tree.plot_tree(clf,class_names=True)
plt.title("Smart Grocery Decision Tree")
plt.show()

print ("end")
