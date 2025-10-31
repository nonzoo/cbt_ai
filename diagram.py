import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np

# Data
metrics = ['Accuracy', 'F1-score', 'Precision']
train_scores = [1.000, 1.000, 1.000]
test_scores = [0.917, 0.915, 0.924]

# DataFrame for easy plotting
df = pd.DataFrame({
    'Metric': metrics,
    'Train': train_scores,
    'Test': test_scores
})

# Bar chart
plt.figure(figsize=(7,4))
df.plot(x='Metric', kind='bar', color=['#4CAF50', '#2196F3'], rot=0)
plt.title('CBT Conversational Model Performance (Train vs Test)')
plt.ylabel('Score')
plt.ylim(0.8, 1.05)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()




# Confusion Matrix data
cm = np.array([
    [21, 7, 0, 2],
    [2, 29, 0, 2],
    [0, 0, 53, 0],
    [1, 0, 1, 42]
])

plt.figure(figsize=(6,5))
sns.heatmap(cm, annot=True, cmap='Blues', fmt='g')
plt.title('Intent Confusion Matrix')
plt.xlabel('Predicted Intent')
plt.ylabel('True Intent')
plt.show()
