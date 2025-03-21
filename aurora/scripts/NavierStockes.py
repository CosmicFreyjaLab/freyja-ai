
import torch
import torch.nn as nn
import torch.autograd as autograd
import numpy as np

# Physics-Informed Neural Network (PINN) for 2D steady Navier-Stokes
class PINN_NavierStokes(nn.Module):
    def __init__(self, layers, nu):
        super(PINN_NavierStokes, self).__init__()
        self.nu = nu

        layer_list = []
        for i in range(len(layers) - 1):
            layer_list.append(nn.Linear(layers[i], layers[i+1]))
            if i < len(layers) - 2:
                layer_list.append(nn.Tanh())
        self.model = nn.Sequential(*layer_list)

    def forward(self, x, y):
        inputs = torch.cat([x, y], dim=1)
        outputs = self.model(inputs)
        u = outputs[:, 0:1]
        v = outputs[:, 1:2]
        p = outputs[:, 2:3]
        return u, v, p

    def compute_residuals(self, x, y):
        x.requires_grad_(True)
        y.requires_grad_(True)
        u, v, p = self.forward(x, y)

        u_x = autograd.grad(u, x, grad_outputs=torch.ones_like(u), create_graph=True)[0]
        u_y = autograd.grad(u, y, grad_outputs=torch.ones_like(u), create_graph=True)[0]
        v_x = autograd.grad(v, x, grad_outputs=torch.ones_like(v), create_graph=True)[0]
        v_y = autograd.grad(v, y, grad_outputs=torch.ones_like(v), create_graph=True)[0]

        u_xx = autograd.grad(u_x, x, grad_outputs=torch.ones_like(u_x), create_graph=True)[0]
        u_yy = autograd.grad(u_y, y, grad_outputs=torch.ones_like(u_y), create_graph=True)[0]
        v_xx = autograd.grad(v_x, x, grad_outputs=torch.ones_like(v_x), create_graph=True)[0]
        v_yy = autograd.grad(v_y, y, grad_outputs=torch.ones_like(v_y), create_graph=True)[0]

        p_x = autograd.grad(p, x, grad_outputs=torch.ones_like(p), create_graph=True)[0]
        p_y = autograd.grad(p, y, grad_outputs=torch.ones_like(p), create_graph=True)[0]

        # Residuals of Navier-Stokes equations
        res_u = u * u_x + v * u_y + p_x - self.nu * (u_xx + u_yy)
        res_v = u * v_x + v * v_y + p_y - self.nu * (v_xx + v_yy)
        res_cont = u_x + v_y

        return res_u, res_v, res_cont

# Example usage
if __name__ == "__main__":
    # Hyperparameters
    nu = 0.01
    layers = [2, 64, 64, 64, 3]  # input: (x, y), output: (u, v, p)

    # Model and optimizer
    model = PINN_NavierStokes(layers, nu)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    # Sample collocation points
    N_f = 10000
    x_f = torch.rand(N_f, 1, requires_grad=True)
    y_f = torch.rand(N_f, 1, requires_grad=True)

    # Training loop
    for epoch in range(10000):
        optimizer.zero_grad()
        res_u, res_v, res_cont = model.compute_residuals(x_f, y_f)

        loss = torch.mean(res_u**2) + torch.mean(res_v**2) + torch.mean(res_cont**2)
        loss.backward()
        optimizer.step()

        if epoch % 500 == 0:
            print(f"Epoch {epoch}, Loss: {loss.item()}")

    torch.save(model.state_dict(), "navier_stokes_pinn.pth")
