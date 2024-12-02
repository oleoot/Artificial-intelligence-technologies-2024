import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Стваорюємо набір необхідних даних
np.random.seed(0)
data = pd.DataFrame({
    'Марка': np.random.choice(['Mazda', 'Toyota', 'BMW', 'Audi', 'Lamborghini'], size=300),
    'Ціна': np.random.uniform(1000, 300000.0, size=300),
    'Кількість': np.random.randint(1, 10000, size=300),
    'Категорія': np.random.choice(['Повсякденні', 'Середній клас', 'Спорткари'], size=300),
    'Клієнт': np.random.choice(['1', '2', '3', '4'], size=300),
    'Прибуток': np.random.uniform(-1000, 100000, size=300),
})

# Замінюємо категоріальних змінних на числові для проведення аналізу.
data = pd.get_dummies(data, columns=['Марка', 'Категорія', 'Клієнт'], drop_first=True)
# 1. Класифікація
# Якщо прибуток більше за 0, то продаж успішний
data['Продано'] = (data['Прибуток'] > 0).astype(int)

# Ділимо дані на навчальну та тестові вибірки
X = data.drop(['Прибуток', 'Продано'], axis=1)
y = data['Продано']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)

# Навчаємо модель класифікації (Random Forest)
clf = RandomForestClassifier(random_state=0)
clf.fit(X_train, y_train)

# Проводимо оцінку моделі
y_pred = clf.predict(X_test)
print("Classification Report:")
print(classification_report(y_test, y_pred))
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# 2. Кластериація
# Проводимо групування товарів відповідно до характеристик
scaler = StandardScaler()
X_scaled = scaler.fit_transform(data.drop(['Прибуток', 'Продано'], axis=1))

# Кластеризація по KMeans
kmeans = KMeans(n_clusters=3, random_state=0)
data['Кластер'] = kmeans.fit_predict(X_scaled)

# Візуалізуємо кластери
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

plt.figure(figsize=(10, 6))
plt.scatter(X_pca[:, 0], X_pca[:, 1], c=data['Кластер'], cmap='viridis')
plt.xlabel('Компонент 1')
plt.ylabel('Компонент 2')
plt.title('Кластеризація марок автомобілів')
plt.colorbar(label='Кластер')
plt.show()

# Відображаємо аналіз кластерів
print(data.groupby('Кластер').mean())
