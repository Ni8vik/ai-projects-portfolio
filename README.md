# ML & Deep Learning Projects

A collection of machine learning and deep learning projects built while learning my way from classic ML into neural networks and deep learning fundamentals. Each folder is a self-contained project — some use frameworks (Keras/TensorFlow), and at least one is implemented entirely from scratch with just NumPy, to actually understand what's happening under the hood rather than treating it as a black box.

## Projects

### 🔢 Handwritten Digit Detection (`handwriten/`)

A neural network trained to classify handwritten digits (MNIST). Takes a 28×28 grayscale image and predicts the digit (0–9).

### 🏠 House Price Prediction (`house_pricing_prediction/`)

A regression model that predicts house prices using the [Melbourne Housing dataset](https://www.kaggle.com/datasets/anthonypino/melbourne-housing-market) from Kaggle. Covers data cleaning, feature handling, and training a model on real-world tabular data.

### 🌀 Spiral Classification — From Scratch (`deeplearning for computer vision/`)

A neural network built **entirely from scratch using NumPy** — no TensorFlow, no Keras, no PyTorch. Generates a configurable number of points along interleaved spiral arms and trains a network to learn the non-linear decision boundary separating them. This one's about understanding forward passes, activations, and backpropagation at the math level, not just calling `.fit()`.

### 📝 Next Word Prediction (`next word prediction/`)

A language model trained on text that generates the next word(s) given a prompt, with an adjustable context window. Model weights are saved separately in `next word predictor weight/`.

### 💬 Chatbot with API Key (`chatbot_with_api_key_app/`)

A working chatbot app built on top of the [GapGPT](https://gapgpt.app/) API (an Iranian-accessible proxy for ChatGPT-style completions). Handles API key-based auth and message exchange in a simple chat interface.

## Why this repo exists

I started with Python and data analysis through **Technosharif** (a Sharif University-affiliated program), and I've been working through numpy, pandas, and scikit-learn before moving deeper into neural networks and deep learning. This repo is where that progression lives — from a from-scratch NumPy classifier to using real frameworks and real-world datasets to building an app powered by an LLM API.

## Setup

Each project may have its own dependencies. In general, you'll need:

```bash
pip install numpy pandas scikit-learn matplotlib
# for the framework-based projects (digit detection, etc.)
pip install tensorflow keras
```

Clone the repo and navigate into whichever project folder you want to run:

```bash
git clone https://github.com/Ni8vik/simple-neural-networks.git
cd simple-neural-networks/<project-folder>
```

## What's next

- Adding proper `requirements.txt` files per project
- More detail per project (architecture, results, sample outputs)
- Moving deeper into deep learning and more complex architectures

## Contact

- LinkedIn: [nima-alimohamadzadeh](https://www.linkedin.com/in/nima-alimohamadzadeh)
- Email: nimaalimohamadzadeh@gmail.com

---

_Part of an ongoing learning journey through Technosharif (Sharif University) — more projects added as I build them._
