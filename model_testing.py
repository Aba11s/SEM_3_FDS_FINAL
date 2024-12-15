# Model

from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier

from sklearn.metrics import confusion_matrix, accuracy_score, balanced_accuracy_score, precision_score, log_loss, roc_auc_score, recall_score, f1_score
from sklearn.metrics import ConfusionMatrixDisplay, RocCurveDisplay, roc_curve
from sklearn.model_selection import train_test_split
from sklearn.inspection import permutation_importance

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv("data/final_pmr.csv")

# feature selection
features = df.iloc[:,2:14]
feature_names = list(features.columns)
print(feature_names)
label = df.iloc[:,14]

X_train, X_test, y_train, y_test = train_test_split(features, label, test_size=0.3, random_state=42)

# model setup
clfs = (
    SVC(kernel='linear', C=1.0, gamma='scale', random_state=42),
    LogisticRegression(random_state=42),
    RandomForestClassifier(random_state=42),
    KNeighborsClassifier(n_neighbors=5)
)

# fitting models
for clf in clfs:
    clf.fit(X_train, y_train)

# simple model class

class Clf():
    def __init__(self, name, y_pred, acc, bal_acc, prc, lgl, rcl, f1, auc):
        self.name = name
        self.y_pred = y_pred
        self.acc_score = acc
        self.acc_bal_score = bal_acc
        self.prc_score = prc
        self.lgl_score = lgl
        self.recl_score = rcl
        self.f_score = f1
        self.auc_roc = auc

clf_preds = []

def f_importance(coef, names):
    imp = coef
    imp,names = zip(*sorted(zip(imp,names)))
    plt.barh(range(len(names)), imp, align='center')
    plt.yticks(range(len(names)), names)
    plt.show()

# model testing
for clf in clfs:
    y_pred = clf.predict(X_test)

    # scores
    acc_score = accuracy_score(y_test, y_pred)
    acc_bal_score = balanced_accuracy_score(y_test, y_pred)
    prc_score = precision_score(y_test, y_pred)
    lgl_score = log_loss(y_test, y_pred)
    rcl_score = recall_score(y_test, y_pred)
    f_score = f1_score(y_test, y_pred)
    au_roc = roc_auc_score(y_test, y_pred)

    clf_preds.append(Clf(type(clf).__name__, y_pred, acc_score, acc_bal_score, prc_score, lgl_score, rcl_score, f_score, au_roc))

    print(f"model: {type(clf).__name__}")
    print(f"acc_score: {acc_score}")
    print(f"balanced_acc: {acc_bal_score}")
    print(f"prc_score: {prc_score}")
    print(f"lgl_score: {lgl_score}")
    print(f"rcl_score: {rcl_score}")
    print(f"f1_score: {f_score}")
    print(f"au_roc: {au_roc}\n")

    # feature importance
    print("\n|----- LINEBREAK -----|\n")


ci = 0
fig, ax = plt.subplots(nrows=2, ncols=2)

for row in ax:
    for col in row:
        display = ConfusionMatrixDisplay(confusion_matrix(y_test, clf_preds[ci].y_pred), display_labels=["t1_win", "t2_win"])
        display.plot(ax=col)
        col.title.set_text(clf_preds[ci].name)
        ci+=1

plt.tight_layout()

# roc curve
plt.figure(2)
for pred in clf_preds:
    fpr, tpr, thresholds = roc_curve(y_test, pred.y_pred)
    plt.plot(fpr, tpr, label=pred.name % pred.auc_roc)

plt.plot([0,1],[0,1], 'k--')
plt.xlim([0.0,1.0])
plt.ylim([0.0,1.0])
plt.xlabel('FPR')
plt.ylabel('TPR')
plt.legend(loc="lower right")

# feature importance based on permutation
plt.figure(3)
'''for clf in clfs:
    print(feature_names)
    perm_imp = permutation_importance(clf, X_test, y_test)

    sorted_idx = perm_imp.importances_mean.argsort()
    plt.barh(feature_names[sorted_idx], perm_imp.importances_mean[sorted_idx])
    plt.xlabel(f"{type(clf).__name__} permutation importance")'''

plt.show()