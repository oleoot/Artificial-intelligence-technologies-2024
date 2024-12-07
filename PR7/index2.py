import numpy as np
import matplotlib.pyplot as plt

# Створюємо випадкові дані
np.random.seed(42)
nums = 100

# Випадкові параметри
area = np.random.rand(nums) * 1000  # площа квм
num_rooms = np.random.randint(1, 6, nums)  # к-сть кімнат від 1 до 5
location = np.random.randint(0, 2, nums)  # 0 - центр, 1 - за центром

# Ціна на основі площі, кімнат та місцезнаходження
price = (300 * area + 15000 * num_rooms - 10000 * location + np.random.randn(nums) * 10000)

# Формуємо дані
X = np.column_stack((area, num_rooms, location))
y = price
X = np.c_[np.ones(nums), X]  # Додаємо стовпець одиниць для вільного члена

# Нормалізуємо дані
X[:, 1] = (X[:, 1] - np.mean(X[:, 1])) / np.std(X[:, 1])  # Площа
X[:, 2] = (X[:, 2] - np.mean(X[:, 2])) / np.std(X[:, 2])  # К-сть кімнат
X[:, 3] = (X[:, 3] - np.mean(X[:, 3])) / np.std(X[:, 3])  # Місцезнаходження

# Ініціалізація коефіцієнтів (випадковими значеннями)
theta = np.random.rand(X.shape[1])

# Функція для обчислення середньоквадратичної помилки (MSE)
def compute_cost(X, y, theta):
    m = len(y)
    predictions = X.dot(theta)
    cost = (1 / (2 * m)) * np.sum(np.square(predictions - y))
    return cost

# Градієнтний спуск
def gradient_descent(X, y, theta, rate, iterations):
    m = len(y)
    cost_history = np.zeros(iterations)

    for i in range(iterations):
        predictions = X.dot(theta)
        errors = predictions - y

        # Theta
        theta -= (rate / m) * (X.T.dot(errors))

        # Функція втрат
        cost_history[i] = compute_cost(X, y, theta)

        # Перевірка на NaN
        if np.isnan(cost_history[i]):
            print("NaN:", i)
            break

    return theta, cost_history

# Параметри навчання
rate = 0.01
iterations = 1000

# Градієнтний спуск
theta_final, cost_history = gradient_descent(X, y, theta, rate, iterations)

# Показуємо зміну значення функції втрат
plt.plot(range(len(cost_history)), cost_history, color='green')
plt.title('Зміна функції втрат (MSE) протягом ітерацій')
plt.xlabel('Ітерації')
plt.ylabel('Функція втрат (MSE)')
plt.grid()
plt.show()

print("Коефіцієнти:", theta_final)
