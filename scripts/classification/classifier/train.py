import numpy as np
import matplotlib.pyplot as plt
import argparse
import pickle

from sklearn import preprocessing
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier


"""
- Classification:
https://scikit-learn.org/stable/auto_examples/classification/plot_classification_probability.html#sphx-glr-auto-examples-classification-plot-classification-probability-py

- Standardization:
Removing the mean value of each feature, 
and scale by dividing with standard deviation.
https://scikit-learn.org/stable/modules/preprocessing.html
"""

parser = argparse.ArgumentParser()
parser.add_argument('-f', type=str, required=True, help="training data: combination of features and manual labels")
args = parser.parse_args()

# Header
with open(args.f, 'r') as f:
    line = f.readline().rstrip('\n')
    header = line.split(' ')[1::]
Nf = len(header)

# Data
# 'ANNOTATION', 'label(id)', 'vol', 'Imax', 'Iavg', 'Istd', 'lx2', 'ly2', 'lz2', 'Rg', 'asph', 'acyl', 'kappa', 'Lmax', 'Lmin', 'Vrs', 'Vre'
#      0           1            2      3        4       5      6      7      8     9      10      11      12       13      14      15    16
X0 = np.loadtxt(args.f, skiprows=1)
idx = np.prod(np.isfinite(X0), axis=1) # remove rows with nan/inf

X   = X0[idx==1, 3::]
y   = X0[idx==1, 0]
y[y!=1] = 0
vol = X0[idx==1, 2]


# Data regularization
scaler = preprocessing.StandardScaler().fit(X)
X_scaled = scaler.transform(X)
"""
Scaled data has zero mean and unit variance
 print(X_scaled.mean(axis=0))
 print(X_scaled.std(axis=0))
"""

# Classifier
classifiers = {
    "Random Forest" : RandomForestClassifier(max_depth=10, n_estimators=100, max_features=3),
}


for index, (name, classifier) in enumerate(classifiers.items()):

    print("\n >>>", name)

    if name == "GPC" or "KNeighbors":
        classifier.fit(X_scaled, y)
    else:
        classifier.fit(X_scaled, y, sample_weight=vol)
    y_pred = classifier.predict(X_scaled)

    accuracy = accuracy_score(y, y_pred, sample_weight=vol)
    print("Accuracy (train) for %s: %0.1f%% " % (name, accuracy * 100))

    C = confusion_matrix(y, y_pred, sample_weight=vol)
    print("confusion_matrix:")
    print(C / np.sum(C))

    with open("classifier.pkl",'wb') as fl:
        pickle.dump(classifier, fl)
    with open("scaler.pkl",'wb') as fl:
        pickle.dump(scaler, fl)

    plt.scatter(X[y_pred==0,9], X[y_pred==0,12], s=5, facecolors='none', edgecolors='b', alpha=0.5)
    plt.scatter(X[y_pred==1,9], X[y_pred==1,12], s=5, facecolors='none', edgecolors='r', alpha=0.5)
    ax = plt.gca()
    #ax.set_xlabel("effective radius")
    #ax.set_ylabel("Vs")
    ax.set_title("%s (%.1f %%)" % (name, accuracy * 100))

plt.tight_layout()
plt.show()


