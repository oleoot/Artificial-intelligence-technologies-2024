import numpy as np
import matplotlib.pyplot as plt

# Створюємо випадкове насіння для відтворюваності
np.random.seed(42)

# Задаємо к-сть точок для кожного класу
dots = 50

# Генерація даних для класу 0 (відхилено)
class_0 = np.random.normal(loc=[2, 2], scale=1.0, size=(dots, 2))

# Генерація даних для класу 1 (схвалено)
class_1 = np.random.normal(loc=[6, 6], scale=1.0, size=(dots, 2))

# Об'єднуємо дані
X = np.vstack((class_0, class_1))
y = np.array([0] * dots + [1] * dots)

# Візуалізація даних
plt.scatter(class_0[:, 0], class_0[:, 1], label='Відхилено', color='red')
plt.scatter(class_1[:, 0], class_1[:, 1], label='Схвалено', color='green')
plt.title('Генеруємо дані для бінарної класифікації')
plt.xlabel('Компонента 1')
plt.ylabel('Компонента 2')
plt.legend()
plt.show()

# Функція сигмоїди
def sigmoid(z):
    return 1 / (1 + np.exp(-z))

# Функція log loss
def log_loss(y_true, prediction):
    epsilon = 1e-15  # Додамо для уникнення log(0)
    prediction = np.clip(prediction, epsilon, 1 - epsilon)  # Кліпуємо значення
    return -np.mean(y_true * np.log(prediction) + (1 - y_true) * np.log(1 - prediction))

class LogisticRegression:
    def __init__(self, learn_rate=0.01, iterations=1000, l2_reg=0.0):
        self.learn_rate = learn_rate
        self.iterations = iterations
        self.l2_reg = l2_reg
        self.weights = None
        self.bias = None
        self.loss_history = []

    def fit(self, X, y):
        samples, n_features = X.shape
        self.weights = np.zeros(n_features)
        self.bias = 0

        for _ in range(self.iterations):
            linear_pred = np.dot(X, self.weights) + self.bias
            y_pred = sigmoid(linear_pred)

            # Рахуємо градієнти
            dw = (1 / samples) * np.dot(X.T, (y_pred - y)) + (self.l2_reg / samples) * self.weights
            db = (1 / samples) * np.sum(y_pred - y)

            # Оновлюємо ваги і зсуву
            self.weights -= self.learn_rate * dw
            self.bias -= self.learn_rate * db

            # Обчислюємо функцію втрат
            loss = log_loss(y, y_pred)
            self.loss_history.append(loss)

    def predict(self, X):
        linear_pred = np.dot(X, self.weights) + self.bias
        y_pred = sigmoid(linear_pred)
        return np.round(y_pred)

# Ініціалізація та тренування моделі
model = LogisticRegression(learn_rate=0.1, iterations=1000, l2_reg=0.01)
model.fit(X, y)

# Візуалізація втрат
plt.plot(range(model.iterations), model.loss_history, label='Функція втрат')
plt.title('Процес навчання')
plt.xlabel('Ітерації')
plt.ylabel('Втрати (log loss)')
plt.legend()
plt.show()

# Оцінка точності моделі
y_pred = model.predict(X)
accuracy = np.mean(y_pred == y)
print(f'Точність моделі: {accuracy:.2f}')

# Візуалізація рішення
plt.scatter(class_0[:, 0], class_0[:, 1], label='Відхилено', color='red')
plt.scatter(class_1[:, 0], class_1[:, 1], label='Схвалено', color='green')

# Будуємо лінію класифікації
x_boundary = np.linspace(0, 8, 200)
y_boundary = -(model.weights[0] * x_boundary + model.bias) / model.weights[1]
plt.plot(x_boundary, y_boundary, label='Лінія розділення', color='blue')

plt.title('Візуалізація рішення')
plt.xlabel('Компонента 1')
plt.ylabel('Компонента 2')
plt.legend()
plt.show()

# Стохастичний градієнтний спуск (StochasticLogisticRegression)
class StochasticLogisticRegression(LogisticRegression):
    def fit(self, X, y):
        samples, n_features = X.shape
        self.weights = np.zeros(n_features)
        self.bias = 0

        for _ in range(self.iterations):
            for i in range(samples):
                rand_index = np.random.randint(0, samples)
                xi = X[rand_index,:].reshape(1, -1)
                yi = y[rand_index]

                linear_pred = np.dot(xi, self.weights) + self.bias
                y_pred = sigmoid(linear_pred)

                dw = (y_pred - yi) * xi.flatten() + (self.l2_reg / samples) * self.weights
                db = (y_pred - yi)

                self.weights -= self.learn_rate * dw
                self.bias -= self.learn_rate * db

                # Обчислення функції втрат на кожній итерації
                loss = log_loss(y, self.predict(X))
                self.loss_history.append(loss)

# Тренування з використанням StochasticLogisticRegression
sgd_model = StochasticLogisticRegression(learn_rate=0.1, iterations=10000, l2_reg=0.01)
sgd_model.fit(X, y)

# Оцінка точності у StochasticLogisticRegression
y_pred_sgd = sgd_model.predict(X)
accuracy_sgd = np.mean(y_pred_sgd == y)
print(f'Точність моделі StochasticLogisticRegression: {accuracy_sgd:.2f}')
