import torch
from gym import spaces


def optimizer_action(
    optimizer: torch.optim.Optimizer, name: str, actions: spaces.Dict
) -> None:
    for g in optimizer.param_groups:
        g[name] = actions[name]


def train(model, optimizer, loss_function, loader, steps, device="cpu"):
    model.train()
    for step in range(steps):
        (data, target) = next(loader)
        data, target = data.to(device), target.to(device)
        output = model(data)
        loss = loss_function(output, target, reduction="none")
        optimizer.zero_grad()
        loss.mean().backward()
        optimizer.step()
    return loss


def test(model, loss_function, loader, device="cpu"):
    model.eval()
    test_losses = []
    with torch.no_grad():
        for data, target in loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            test_losses.append(loss_function(output, target, reduction="none"))
    return torch.cat(test_losses)
