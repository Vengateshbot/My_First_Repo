import numpy as np

# Define activation functions
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def tanh(x):
    return np.tanh(x)

# Initialize weights and biases with small random values
weights = np.random.randn(2, 2) * 0.1
biases = np.random.randn(2) * 0.1

# Define the neural network
def neural_network(inputs, activation="sigmoid"):
    hidden = np.dot(inputs, weights) + biases
    if activation == "sigmoid":
        outputs = sigmoid(hidden)
    elif activation == "tanh":
        outputs = tanh(hidden)
    else:
        raise ValueError("Invalid activation function. Choose 'sigmoid' or 'tanh'.")
    return outputs

# Define loss function (mean squared error)
def mean_squared_error(predicted, target):
    return np.mean((predicted - target)**2)

# Generate training data (XOR gate dataset)
inputs = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
targets = np.array([[0, 0], [1, 0], [1, 0], [0, 1]])

# Define training parameters
learning_rate = 0.1
epochs = 500

# Training loop
for epoch in range(epochs):
    # Forward pass
    outputs = neural_network(inputs)

    # Calculate loss
    loss = mean_squared_error(outputs, targets)

    # Backpropagation (simplified version)
    errors = outputs - targets
    hidden_errors = np.dot(errors, weights.T)
    weights -= learning_rate * np.dot(inputs.T, hidden_errors)
    biases -= learning_rate * hidden_errors.mean(axis=0) 

    # Print progress
    if epoch % 100 == 0:
        print(f"Epoch: {epoch+1}, Loss: {loss:.4f}")

# Test the network with new inputs
test_inputs = np.array([[0.8, 0.9], [0.8, 0.2]])
predictions = neural_network(test_inputs)
print("\nPredictionsss:")
print(predictions)
