import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

# Створюємо випадкові дані
np.random.seed(42)
nums = 300
X = np.linspace(-3, 3, nums).reshape(-1, 1)
y = 0.5 * X**2 + X + 2 + np.random.randn(nums, 1) * 0.5

# Додаємо поліноміальні ознаки
X_poly = np.c_[X, X**2]

# Розділення даних на навчальну та тестову вибірки
X_train, X_test, y_train, y_test = train_test_split(X_poly, y, test_size=0.2, random_state=42)

# Обчислення середньоквадратичної похибки
def compute_mse(y_true, y_pred):
    return np.mean((y_true - y_pred) ** 2)

# Метод градієнтного спуску для поліноміальної регресії
def polynomial_gradient_descent(X, y, rate, iterations):
    m = X.shape[0]
    n = X.shape[1]
    theta = np.random.randn(n, 1)
    loss_history = []

    for iteration in range(iterations):
        gradients = 2 / m * X.T.dot(X.dot(theta) - y)
        theta -= rate * gradients
        if iteration % 100 == 0:
            y_pred = X.dot(theta)
            loss = compute_mse(y, y_pred)
            loss_history.append(loss)

            # Візуалізація результатів
            plt.scatter(X[:, 0], y, color='green', alpha=0.5, label='Спостереження')
            X_range = np.linspace(-3, 3, 100).reshape(-1, 1)
            X_range_poly = np.c_[X_range, X_range**2]
            y_range_pred = X_range_poly.dot(theta)
            plt.plot(X_range, y_range_pred, color='orange', label='Поліноміальна модель')
            plt.title(f'Ітерація: {iteration}')
            plt.xlabel('X')
            plt.ylabel('y')
            plt.legend()
            plt.show()

    return theta, loss_history

# Параметри навчання
rate = 0.01
iterations = 1000

# Градієнтний спуск
theta_poly, loss_history_poly = polynomial_gradient_descent(X_train, y_train, rate, iterations)

# Оцінка точності поліноміальної моделі
y_pred_test_poly = X_test.dot(theta_poly)
mse_test_poly = compute_mse(y_test, y_pred_test_poly)

print(f"Оптимальні параметри: {theta_poly.flatten()}")
print(f"Середньоквадратична похибка (поліноміальна): {mse_test_poly:.4f}")

# Порівняння з лінійною регресією:
# Для лінійної регресії
theta_linear = np.random.randn(X_train.shape[1], 1)
for iteration in range(iterations):
    gradients = 2 / X_train.shape[0] * X_train.T.dot(X_train.dot(theta_linear) - y_train)
    theta_linear -= rate * gradients

y_pred_test_linear = X_test.dot(theta_linear)
mse_test_linear = compute_mse(y_test, y_pred_test_linear)

print(f"Середньоквадратична похибка (лінійна): {mse_test_linear:.4f}")

# Візуалізація кривих функції втрат
plt.figure(figsize=(10, 6))
plt.plot(loss_history_poly, label='Поліноміальна модель', color='orange')
plt.title('Збіжність функції втрат для поліноміальної регресії')
plt.xlabel('Ітерації (кожні 100)')
plt.ylabel('Середньоквадратична похибка')
plt.legend()
plt.grid()
plt.show()
