import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_moons
from sklearn.model_selection import train_test_split

# Створюємо випадкові дані
X, y = make_moons(n_samples=1000, noise=0.1, random_state=42)
# Перетворення y в колонковий вектор
y = y.reshape(-1, 1)

# Розділення даних на навчальну та тестову вибірки
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# функція sigmoid
def sigmoid(z):
    return 1 / (1 + np.exp(-z))

# Похідна функції sigmoid
def sigmoid_derivative(z):
    return sigmoid(z) * (1 - sigmoid(z))

# Функція для обчислення логістичної втрати
def compute_loss(y_true, prediction):
    m = y_true.shape[0]
    return -1 / m * np.sum(y_true * np.log(prediction + 1e-15) + (1 - y_true) * np.log(1 - prediction + 1e-15))

# Нейронна мережа з одним прихованим прошарком
class NeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size, rate):
        self.weights_input_hidden = np.random.randn(input_size, hidden_size) * 0.01
        self.weights_hidden_output = np.random.randn(hidden_size, output_size) * 0.01
        self.rate = rate

    def forward(self, X):
        self.hidden_input = np.dot(X, self.weights_input_hidden)
        self.hidden_output = sigmoid(self.hidden_input)
        self.final_input = np.dot(self.hidden_output, self.weights_hidden_output)
        self.final_output = sigmoid(self.final_input)
        return self.final_output

    def backward(self, X, y):
        m = X.shape[0]
        output_error = self.final_output - y
        hidden_error = output_error.dot(self.weights_hidden_output.T) * sigmoid_derivative(self.hidden_input)
        d_weights_hidden_output = self.hidden_output.T.dot(output_error) / m
        d_weights_input_hidden = X.T.dot(hidden_error) / m
        self.weights_hidden_output -= self.rate * d_weights_hidden_output
        self.weights_input_hidden -= self.rate * d_weights_input_hidden

    def train(self, X, y, iterations):
        self.loss_history = []
        for epoch in range(iterations):
            # Прямий прохід
            self.forward(X)
            # Зворотній прохід
            self.backward(X, y)
            # Обчислення втрат
            loss = compute_loss(y, self.final_output)
            self.loss_history.append(loss)
            # Виведення інформації
            if epoch % 50 == 0:
                print(f"Epoch {epoch}, Loss: {loss:.4f}")

# Параметри моделі
input_size = 2    # Кількість ознак
hidden_size = 4   # Кількість нейронів у прихованому прошарку
output_size = 1   # Вихідний нейрон
rate = 0.1
iterations = 1000

# Навчання нейронної мережі
nn = NeuralNetwork(input_size, hidden_size, output_size, rate)
nn.train(X_train, y_train, iterations)

# Візуалізація графіка втрат
plt.plot(nn.loss_history)
plt.title('Графік втрат')
plt.xlabel('Ітерації')
plt.ylabel('Втрата')
plt.grid()
plt.show()

# Оцінка точності моделі
y_pred_train = nn.forward(X_train)
y_pred_train_class = (y_pred_train > 0.5).astype(int)
train_accuracy = np.mean(y_pred_train_class == y_train)
print(f"Точність на навчальних даних: {train_accuracy:.4f}")

y_pred_test = nn.forward(X_test)
y_pred_test_class = (y_pred_test > 0.5).astype(int)
test_accuracy = np.mean(y_pred_test_class == y_test)
print(f"Точність на тестових даних: {test_accuracy:.4f}")

# Порівняння з логістичною регресією
from sklearn.linear_model import LogisticRegression

# Логістична регресія
log_reg = LogisticRegression()
log_reg.fit(X_train, y_train)
log_reg_train_accuracy = log_reg.score(X_train, y_train)
log_reg_test_accuracy = log_reg.score(X_test, y_test)

print(f"Точність регресії на навчальних даних: {log_reg_train_accuracy:.4f}")
print(f"Точність регресії на тестових даних: {log_reg_test_accuracy:.4f}")
