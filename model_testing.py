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
from time import process_time

df = pd.read_csv("data/final_pmr.csv")

# feature selection
pruned = [3,4,5,6,11,12]

features = df.iloc[:,pruned]
feature_names = np.array(features.columns)
print(feature_names)
label = df.iloc[:,14]

X_train, X_test, y_train, y_test = train_test_split(features, label, test_size=0.3, random_state=42)

# model setup
clfs = (
    SVC(kernel='linear', C=1, gamma='scale', random_state=42),
    LogisticRegression(solver='liblinear', random_state=42),
    RandomForestClassifier(n_estimators= 100, min_samples_split=2, min_samples_leaf=1, random_state=42),
    KNeighborsClassifier(p=3, n_neighbors=5)
)

# fitting models
for clf in clfs:
    start = process_time()
    clf.fit(X_train, y_train)
    end = process_time()
    print(f"time: {end-start}")

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

clf_scores = []
scores = []

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

    clf_scores.append(Clf(type(clf).__name__, y_pred, acc_score, acc_bal_score, prc_score, lgl_score, rcl_score, f_score, au_roc))
    scores.append([acc_score, prc_score, rcl_score, f_score, au_roc])

    print(f"model: {type(clf).__name__}")
    print(f"acc_score: {acc_score}")
    print(f"balanced_acc: {acc_bal_score}")
    print(f"prc_score: {prc_score}")
    print(f"lgl_score: {lgl_score}")
    print(f"rcl_score: {rcl_score}")
    print(f"f1_score: {f_score}")
    print(f"au_roc: {au_roc}\n")
    print("\n|----- LINEBREAK -----|\n")


# VISUALIZATIONS

visualize = True

if visualize:
    # figure 1 | accuracy figures
    plt.figure(1)

    v_count = len(clf_scores)
    x = np.arange(5)
    width = 0.2

    for i in range(v_count):
        plt.bar(x + i * width, scores[i], width=width, label=clf_scores[i].name)

    plt.xticks(x + (v_count-1) * width/2, ['accuracy', 'precision', 'recall', 'f-score', 'auc-roc'])
    plt.yticks(list(y/100 for y in range(0,100,5)))
    plt.legend([score.name for score in clf_scores], loc = 'lower right')

    # figure 2 | confusion matrix
    ci = 0
    fig, ax = plt.subplots(nrows=2, ncols=2)

    for row in ax:
        for col in row:
            display = ConfusionMatrixDisplay(confusion_matrix(y_test, clf_scores[ci].y_pred), display_labels=["t1_win", "t2_win"])
            display.plot(ax=col)
            col.title.set_text(clf_scores[ci].name)
            ci+=1

    plt.tight_layout()

    # figure 3 | ROC curve
    plt.figure(3)
    for pred in clf_scores:
        fpr, tpr, thresholds = roc_curve(y_test, pred.y_pred)
        plt.plot(fpr, tpr, label = pred.name % pred.auc_roc)

    plt.plot([0,1],[0,1], 'k--')
    plt.xlim([0.0,1.0])
    plt.ylim([0.0,1.0])
    plt.xlabel('FPR')
    plt.ylabel('TPR')
    plt.legend(loc="lower right")

    # figure 4 | Feature importance based on permutation
    clf_names = [type(clf).__name__ for clf in clfs]

    importances = {}
    for clf, name in zip(clfs, clf_names):
        result = permutation_importance(clf, X_test, y_test, n_repeats=30, random_state=0)
        importances[name] = result.importances_mean

    importance_df = pd.DataFrame(importances, index=feature_names)
    importance_df = importance_df.transpose()

    num_features = importance_df.shape[1]
    bar_width = 0.2
    y = np.arange(num_features)

    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot each model's importance
    for i, model in enumerate(importance_df.index):
        ax.barh(y-0.2 + i * bar_width, importance_df.loc[model], height=bar_width, label=model)

    # Customize the plot
    ax.set_xlabel('Permutation Importance')
    ax.set_title('Permutation Importance of Models')
    ax.set_yticks(y + bar_width / 2)
    ax.set_yticklabels(importance_df.columns)
    ax.legend(title='Models')
    ax.grid(axis='y')
    ax.axvline(x=0, color='black')
    ax.legend(loc='lower right')

    plt.tight_layout()  # Adjust layout
    plt.show()


# DATA OUTPUTS


# saving accuracy outputs into csv
model_df = pd.DataFrame(
    columns=[
        'model_name',
        'accuracy_score',
        'balanced_acc_score',
        'precision_score',
        'recall_score',
        'f_score',
        'roc_auc',
        'log_loss'
    ]
)

for scores in clf_scores:
    model_df.loc[len(model_df)] = [scores.name, scores.acc_score, scores.acc_bal_score, scores.prc_score, scores.recl_score, scores.f_score, scores.auc_roc, scores.lgl_score]

# model accuracy csv file
model_df.to_csv('output/accuracy-output-2.csv')