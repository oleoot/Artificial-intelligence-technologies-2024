import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

# Створюємо випадкові дані
np.random.seed(42)
nums = 300
X1 = 2 * np.random.rand(nums, 1)
X2 = 2 * np.random.rand(nums, 1)
y = 4 + 3 * X1 + 5 * X2 + np.random.randn(nums, 1)

# Додаємо стовпець для вільного члена
X_b = np.c_[np.ones((nums, 1)), X1, X2]

# Розділення даних на навчальну та тестову вибірки
X_train, X_test, y_train, y_test = train_test_split(X_b, y, test_size=0.2, random_state=42)

# Обчислення середньоквадратичної похибки (MSE)
def compute_mse(y_true, y_pred):
    return np.mean((y_true - y_pred) ** 2)

# Метод градієнтного спуску для множинної лінійної регресії
def gradient_descent(X, y, rate, iterations):
    m = X.shape[0]
    n = X.shape[1]
    theta = np.random.randn(n, 1)
    loss_history = []

    for iteration in range(iterations):
        gradients = 2 / m * X.T.dot(X.dot(theta) - y)
        theta -= rate * gradients
        if iteration % 50 == 0:
            y_pred = X.dot(theta)
            loss = compute_mse(y, y_pred)
            loss_history.append(loss)

    return theta, loss_history

# Параметри навчання
rate = 0.01
iterations = 1000

# Градієнтний спуск
theta, loss_history = gradient_descent(X_train, y_train, rate, iterations)

# Оцінюємо точність моделі
y_pred_test = X_test.dot(theta)
mse_test = compute_mse(y_test, y_pred_test)

print(f"Оптимальні параметри: {theta.flatten()}")
print(f"Середньоквадратична похибка: {mse_test:.4f}")

# Візуалізація графіка збіжності
plt.figure(figsize=(10, 6))
plt.plot(loss_history, label='Функція втрат', color='red')
plt.title('Збіжність функції втрат')
plt.xlabel('Ітерації')
plt.ylabel('Середньоквадратична похибка')
plt.legend()
plt.grid()
plt.show()
