import numpy as np

# impurity funcions
def gini(data):
      unique = np.unique_counts(data).counts
      prob = unique/ len(data)
      return 1 - np.sum(np.pow(prob, 2))

def entropy(data):
      if len(data)==0:
            return 0
      unique = np.unique_counts(data).counts
      prob = unique/ len(data)
      return -(np.sum(prob * np.log2(prob)))
#gain funcions
def gain(parent, *child, method=gini):
      if len(parent)==0:
            return 0.0
      return method(parent) - sum(len(i)/ len(parent) * method(i) for i in child)


# best split function (one feature)
def best_split_numeric(data, label, method=gini):
      u_data = np.unique(data)
      tresh = (u_data[1:] + u_data[:-1]) /2
      best_gain, best_t = -1.0, None
      for t in tresh:
            mask = data >= t
            left, right = label[mask] , label[~mask]
            if len(left)== 0 or len(right)==0:
                  continue
            
            g = gain(label, left, right, method=method)
            if g > best_gain:
                  best_t, best_gain = t , g
      return  best_t, best_gain

def best_split_categorical(data, label, method=gini):
      best_gain, best_v = -1.0, None
      for d in np.unique(data):
            mask = data == d
            left, right = label[mask] , label[~mask]
            if len(left)== 0 or len(right)==0:
                  continue
            g = gain(label, left, right, method=method)
            if g > best_gain:
                  best_v, best_gain = d , g
      return  best_v, best_gain


#best split function (multiple feature)
def best_split_multiple(data, y, method=gini):
      best = (None, None, -1.0, False)
      columns = data.columns
      for col in columns:
            x = data[col].to_numpy()
            if np.issubdtype(x.dtype, np.number):
                  value, g = best_split_numeric(x, y, method=method)
                  is_cat = False
            else:
                  value, g = best_split_categorical(x, y, method=method)
                  is_cat = True
            
            if value is not None and g > best[2]:
                  best = (col, value, g, is_cat)
                  
      return best


#node class
class Node:
      def __init__(self, feature=None, value=None, is_categorical=None, left=None , right=None, prediction=None):
            
            if prediction is not None:

                  if any(i is not None for i in [feature, value, is_categorical, left, right]):
                        raise ValueError("a leaf must not have split fields")
                  self.feature = None
                  self.value = None
                  self.is_categorical = None
                  self.left = None
                  self.right = None
                  self.prediction = prediction
                  self.is_leaf = True
      
            else:
                  if any(i is None for i in [left, right]):
                        raise ValueError("the internal node must have both left and right branch")
                  
                  if feature is None:
                        raise ValueError("as internal node must have a feature, not None")
                  
                  if value is None:
                        raise ValueError("as internal node must have a value, not None")
                  
                  if is_categorical is None:
                        raise ValueError("as internal node must have a is_categorical, not None")
                  
                  self.feature = feature
                  self.value = value
                  self.is_categorical = is_categorical
                  self.left = left
                  self.right = right
                  self.prediction = None
                  self.is_leaf = False


def majority_helper(value):
      if len(value) == 0:
            raise ValueError("majority_helper got no labels")
      unique_values, unique_counts= np.unique(value, return_counts=True)
      most_repeated = unique_values[np.argmax(unique_counts)]
      
      return most_repeated
            
            
## work for one value or a numpy array not plain lists so the inputs mustn't be python lists
def mask_helper(column, split_value, is_categorical):
      if is_categorical is None:
            raise ValueError("the is_categorical must have a value for which to detect numeric from categoric")
      elif is_categorical:
            return column == split_value
      else:
            return column >= split_value
      
      
def build(data, label, current_depth, min_samples_split=2, max_depth=np.inf, best_split_method=gini):
      if (len(np.unique(label)) == 1 or current_depth >= max_depth or len(label) < min_samples_split):
            return Node(prediction=majority_helper(label))
      
      col, value, g, is_cat = best_split_multiple(data, label, method=best_split_method)
      if col is None or g <= 0:
            return Node(prediction=majority_helper(label))
      
      mask = mask_helper(data[col].to_numpy(), value, is_cat)
      left_d, right_d = data[mask], data[~mask]
      left_l, right_l = label[mask], label[~mask]
      
      left_subtree = build(left_d, left_l, current_depth=current_depth+1, min_samples_split=min_samples_split, max_depth=max_depth, best_split_method=best_split_method)
      right_subtree = build(right_d, right_l, current_depth=current_depth+1, min_samples_split=min_samples_split, max_depth=max_depth, best_split_method=best_split_method)
      
      return Node(feature=col, value=value, is_categorical=is_cat, left=left_subtree, right=right_subtree)
      
def predict_single(root_node, row):
      if root_node.is_leaf:
            return root_node.prediction
      
      if mask_helper(row[root_node.feature], root_node.value, root_node.is_categorical):
            return predict_single(root_node=root_node.left, row=row)
      
      return predict_single(root_node=root_node.right, row=row)


def predict_multiple(root, dataframe):
      if dataframe is None:
            raise ValueError("the dataframe is None")
      if dataframe.empty:
            return np.array([])
      else:
            predictions = np.array(dataframe.apply(lambda row: predict_single(root_node=root, row=row), axis=1))
            return predictions


class decisiontree:
      def __init__(self, max_depth= np.inf, min_sample_split = 2, method=gini):
            if max_depth < 0:
                  raise ValueError("max_depth can't be negative")
            if min_sample_split <= 1:
                  raise ValueError("min_sample_split needs to be larger that 1")
            self.max_depth = max_depth
            self.min_sample_split = min_sample_split
            self.method = method
            self.root = None
            
      def fit(self, x, y):
            if len(x)==0:
                  raise ValueError("the dataframe is empty")
            if len(y)==0:
                  raise ValueError("the target is empty")
            if not len(x)==len(y):
                  raise ValueError("inconsistance size, the size of the dataframe doesn't match the target")
            
            self.root = build(x, np.asarray(y), current_depth=0, min_samples_split=self.min_sample_split, max_depth=self.max_depth, best_split_method=self.method)
            return self
      def predict(self, x):
            if self.root is None:
                  raise ValueError("call fit before predicting")
            return predict_multiple(self.root, x)