import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# Вхідні дані
data = {
    'Year': [2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024], # Роки
    'SquareMeterPrice': [1800, 1700, 1600, 1500, 1400, 1200, 1000, 900, 1200, 1250, 1350, 1400, 1500, 900, 1100, 1400] # Середня ціна 1квм в Києві в USD
}

# Створюємо DataFrame
df = pd.DataFrame(data)
# Перетворюємо дані в необхіний для нас формат
X = df[['Year']]  # Незалежна змінна
y = df['SquareMeterPrice']  # Залежна змінна

# Ділимо дані на тренувальну і тестову вибірки
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Модельна регресія
model = LinearRegression()

# Навчаємо модель
model.fit(X_train, y_train)

# Створюємо прогноз
y_pred = model.predict(X_test)

# Оцінюємо модель
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

# Робимо прогнози по вибраним рокам
prediction2025 = model.predict([[2025]])
prediction2026 = model.predict([[2026]])
prediction2027 = model.predict([[2027]])
print(f"Ціна 1квм в Україні на 2025 рік: {round(prediction2025[0])}")
print(f"Ціна 1квм в Україні на 2026 рік: {round(prediction2026[0])}")
print(f"Ціна 1квм в Україні на 2027 рік: {round(prediction2027[0])}")
