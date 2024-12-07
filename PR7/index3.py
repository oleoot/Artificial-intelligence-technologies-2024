import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

# Створюємо випадкові дані
np.random.seed(42)
nums = 200
X = 2 * np.random.rand(nums, 1)
y = 4 + 3 * X + np.random.randn(nums, 1)

# Додавання стовпця одиниць для вільного члена
X_b = np.c_[np.ones((nums, 1)), X]

# Розділення даних на навчальну та тестову частини
X_train, X_test, y_train, y_test = train_test_split(X_b, y, test_size=0.2, random_state=42)

# Функція для обчислення середньоквадратичної похибки (MSE)
def mse(y_true, prediction):
    return np.mean((y_true - prediction) ** 2)

# Стохастичний градієнтний спуск (SGD)
def stochastic_gradient_descent(X, y, learning_rate, iterations):
    m = X.shape[0]
    theta = np.random.randn(2, 1)  # Ініціалізація параметрів
    loss_history = []

    for iteration in range(iterations):
        for i in range(m):
            random_index = np.random.randint(m)
            xi = X[random_index:random_index + 1]
            yi = y[random_index:random_index + 1]
            # Обчислення градієнтів
            gradients = 2 * xi.T.dot(xi.dot(theta) - yi)
            theta -= learning_rate * gradients

        prediction = X.dot(theta)
        loss = mse(y, prediction)
        loss_history.append(loss)

    return theta, loss_history

# Міні-пакетний градієнтний спуск
def mini_batch(X, y, learning_rate, iterations, batch_size):
    m = X.shape[0]
    theta = np.random.randn(2, 1)  # Ініціалізація параметрів
    loss_history = []

    for iteration in range(iterations):
        indices = np.random.permutation(m)  # Перемішування индексов
        X_shuffled = X[indices]
        y_shuffled = y[indices]

        for i in range(0, m, batch_size):
            xi = X_shuffled[i:i + batch_size]
            yi = y_shuffled[i:i + batch_size]
            # Обчислення градієнтів
            gradients = 2 / batch_size * xi.T.dot(xi.dot(theta) - yi)
            theta -= learning_rate * gradients

        prediction = X.dot(theta)
        loss = mse(y, prediction)
        loss_history.append(loss)

    return theta, loss_history

# Градієнтний спуск з моментом
def gradient_descent(X, y, learning_rate, iterations, momentum=0.9):
    m = X.shape[0]
    theta = np.random.randn(2, 1)  # Ініціалізація параметрів
    velocity = np.zeros_like(theta)  # Ініціалізація швидкості
    loss_history = []
    # Обчислення градієнтів
    for iteration in range(iterations):
        gradients = 2 / m * X.T.dot(X.dot(theta) - y)
        velocity = momentum * velocity - learning_rate * gradients
        theta += velocity  # Оновлення параметрів

        prediction = X.dot(theta)
        loss = mse(y, prediction)
        loss_history.append(loss)

    return theta, loss_history

# Параметри навчання
learning_rate = 0.01
iterations = 1000
batch_size = 20

# Робота моделей
theta_sgd, loss_history_sgd = stochastic_gradient_descent(X_train, y_train, learning_rate, iterations)
theta_mbgd, loss_history_mbgd = mini_batch(X_train, y_train, learning_rate, iterations, batch_size)
theta_momentum, loss_history_momentum = gradient_descent(X_train, y_train, learning_rate, iterations)

# Середньоквадратична похибка
y_pred_sgd = X_test.dot(theta_sgd)
mse_sgd = mse(y_test, y_pred_sgd)

y_pred_mbgd = X_test.dot(theta_mbgd)
mse_mbgd = mse(y_test, y_pred_mbgd)

y_pred_momentum = X_test.dot(theta_momentum)
mse_momentum = mse(y_test, y_pred_momentum)

print(f"SGD: {mse_sgd:.4f}")
print(f"Міні-пакетний: {mse_mbgd:.4f}")
print(f"З моментом: {mse_momentum:.4f}")

# Візуалізація функції втрат
plt.figure(figsize=(10, 6))
plt.plot(loss_history_sgd, label='SGD', color='red')
plt.plot(loss_history_mbgd, label='Міні-пакетний', color='orange')
plt.plot(loss_history_momentum, label='З моментом', color='blue')
plt.title('Втрати для різних методів градієнтного спуску')
plt.xlabel('Ітерації')
plt.ylabel('Середньоквадратична похибка')
plt.legend()
plt.grid()
plt.show()
