import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import statsmodels.api as sm

# Генеруємо довільний набір даних
np.random.seed(0)
data = pd.DataFrame({
    "Вік": np.random.randint(30, 80, size=299),
    "Анемія": np.random.randint(0, 2, size=299),
    "Креатинін_фосфокіназа": np.random.randint(50, 3000, size=299),
    "Діабет": np.random.randint(0, 2, size=299),
    "Фракція_викиду": np.random.randint(20, 80, size=299),
    "Високий_тиск": np.random.randint(0, 2, size=299),
    "Тромбоцити": np.random.uniform(100, 500, size=299),
    "Сироватковий_креатинін": np.random.uniform(0.5, 5.0, size=299),
    "Сироватковий_натрій": np.random.randint(120, 140, size=299),
    "Стать": np.random.randint(0, 2, size=299),
    "Куріння": np.random.randint(0, 2, size=299),
    "Час": np.random.randint(30, 300, size=299),
    "Смертність": np.random.randint(0, 2, size=299)
})

# Статистика
print(data.describe())

# Візуалізація розподілу змінних
plt.figure(figsize=(10, 6))
sns.histplot(data=data, x="Вік", hue="Смертність", multiple="stack")
plt.title("Розподіл віку пацієнтів залежно від смертності")
plt.xlabel("Вік")
plt.ylabel("Кількість")
plt.show()

# Логістична регресія
X = data.drop("Смертність", axis=1)
y = data["Смертність"]

# Додаємо константу для перехоплення
X = sm.add_constant(X)
log_reg_model = sm.Logit(y, X).fit()
print(log_reg_model.summary())

# Кластеризуємо пацієнтів
scaler = StandardScaler()
data_scaled = scaler.fit_transform(data.drop("Смертність", axis=1))

# Використовуємо KMeans для кластеризації
kmeans = KMeans(n_clusters=3, random_state=0)
data['cluster'] = kmeans.fit_predict(data_scaled)

# Візуалізуємо кластери
pca = PCA(n_components=2)
data_pca = pca.fit_transform(data_scaled)
plt.figure(figsize=(10, 6))
plt.scatter(data_pca[:, 0], data_pca[:, 1], c=data['cluster'], cmap='viridis')
plt.title("Кластери пацієнтів")
plt.xlabel("Компонент 1")
plt.ylabel("Компонент 2")
plt.colorbar(label="Кластер")
plt.show()
