import pandas as pd
import numpy as np
import pickle
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engines.phish.feature_extractor import extract_features
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report

print("Loading datasets...")

# Load phishing URLs (PhishTank format)
phish_df = pd.read_csv('data/phishing_dataset.csv', usecols=['url'], nrows=5000)
phish_df['label'] = 1  # 1 = phishing

# Load legitimate domains (Tranco format: rank, domain -- NO header row)
legit_df = pd.read_csv('data/top-1m.csv', header=None, names=['rank', 'domain'], nrows=5000)
legit_df['url'] = 'https://' + legit_df['domain']
legit_df = legit_df[['url']]
legit_df['label'] = 0  # 0 = legitimate

# Combine
df = pd.concat([phish_df, legit_df], ignore_index=True)
df = df.dropna(subset=['url'])
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

print(f"Total URLs: {len(df)} ({df['label'].sum()} phishing, {(df['label']==0).sum()} legitimate)")
print("Extracting features... (this takes a few minutes)")

feature_list = []
labels = []
failed = 0

for i, row in df.iterrows():
    try:
        result = extract_features(str(row['url']))
        features = result['features']
        feature_list.append(list(features.values()))
        labels.append(row['label'])
    except Exception:
        failed += 1

    if i % 500 == 0:
        print(f"  Processed {i}/{len(df)} URLs...")

print(f"Feature extraction complete. Failed: {failed}")

X = np.array(feature_list)
y = np.array(labels)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\nTraining set: {len(X_train)} URLs")
print(f"Testing set:  {len(X_test)} URLs")
print("\nTraining Random Forest model...")

model = RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print("\n" + "="*50)
print("MODEL EVALUATION RESULTS")
print("="*50)
print(f"Accuracy:  {accuracy_score(y_test, y_pred)*100:.2f}%")
print(f"Precision: {precision_score(y_test, y_pred)*100:.2f}%")
print(f"Recall:    {recall_score(y_test, y_pred)*100:.2f}%")
print(f"F1 Score:  {f1_score(y_test, y_pred)*100:.2f}%")
print("\nDetailed Report:")
print(classification_report(y_test, y_pred, target_names=['Legitimate', 'Phishing']))

os.makedirs('ml', exist_ok=True)
with open('ml/phish_model.pkl', 'wb') as f:
    pickle.dump(model, f)

feature_names = [
    'url_length', 'dot_count', 'hyphen_count', 'digit_count',
    'has_ip_address', 'has_at_symbol', 'subdomain_count',
    'https_in_path', 'url_entropy', 'suspicious_keyword_count',
    'path_depth', 'query_param_count'
]
with open('ml/feature_names.pkl', 'wb') as f:
    pickle.dump(feature_names, f)

print("\n✅ Model saved to ml/phish_model.pkl")
print("✅ Training complete!")