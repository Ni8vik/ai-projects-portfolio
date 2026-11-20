# Decision Tree From Scratch 🌳

I'm learning machine learning, and the first model we covered in my course was a decision tree. I thought it would be fun to try writing one myself instead of jumping straight into scikit-learn.

So this is my attempt at building a decision tree using NumPy and pandas. It's definitely not meant to replace scikit-learn. I mainly wanted to understand what happens when the tree decides where to split, and how it makes a prediction afterward.

## What I built

The tree can:

- calculate Gini impurity and entropy
- find splits using information gain
- work with numerical and simple categorical columns
- build a tree recursively
- stop based on depth or minimum samples
- predict classes for new rows

It's a classification tree, not a regression tree.

## Files

- **`model.py`** — my actual decision-tree code taken from the original notebook. I kept the functions, class names, and approach rather than redesigning the algorithm.
- **`notebook.ipynb`** — the steps I took while building it, my early tests, and some plots that help explain the ideas.
- **`test.ipynb`** — simple `assert` checks to see if things work.
- **`example.ipynb`** — comparing my tree with scikit-learn on Iris and Titanic, with separate plots for accuracy, F1, speed, and confusion matrices.
- **`README.md`** — this file.

## Running it

I used Python, NumPy, pandas, matplotlib, seaborn, scikit-learn, and Jupyter.

```bash
pip install numpy pandas matplotlib seaborn scikit-learn jupyter
jupyter notebook
```

You can open the notebooks and run the cells from top to bottom. Keep the files in the same folder so `from model import ...` works.

Here's a basic example:

```python
import pandas as pd
from model import decisiontree

X = pd.DataFrame({"hours_studied": [1, 2, 3, 7, 8, 9]})
y = pd.Series([0, 0, 0, 1, 1, 1])

my_tree = decisiontree(max_depth=3)
my_tree.fit(X, y)
print(my_tree.predict(X))
```

A small detail from my implementation: on numerical splits, values **greater than or equal to** the threshold go to the left. For categorical splits, the matching category goes to the left.

## Comparing it to scikit-learn

In `example.ipynb`, I use the same train/test split for each model and compare:

- accuracy, precision, recall, and F1 score
- training time and prediction time
- confusion matrices

Iris comes with scikit-learn, so that part works offline. For Titanic I use the public CSV from [DataScienceDojo](https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv). If it cannot be downloaded, save the file as `titanic.csv` in this folder and rerun the notebook.

To keep the comparison fair, Titanic's missing numbers are filled using the **training data**, and categorical columns are encoded the same way for both models. The models use Gini impurity and the same maximum depth. The timing numbers will change depending on the computer.

## A few things I haven't done

There are still some limitations. My code expects pandas DataFrames for features and a pandas Series for the target. It doesn't handle missing values by itself, and I haven't added pruning, probability predictions, or optimizations. For real data like Titanic, I prepare the data before passing it to the tree.

I also haven't tried to make the code as fast as scikit-learn. It loops through possible splits in Python, which gets slow on larger datasets.

## Why I made this

The main thing I wanted was to understand decision trees instead of treating them as a black box. Writing the impurity calculations, the splits, and the recursive nodes helped a lot. I plan to come back to this project as I learn more ML.
