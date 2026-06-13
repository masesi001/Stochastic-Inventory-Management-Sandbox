"""Stochastic samplers."""
import numpy as np

class Distributions:
    def __init__(self, seed: int = 42):
        self.rng = np.random.default_rng(seed)

    def demand(self, lam: float, deterministic: bool = False) -> int:
        if deterministic or lam <= 0:
            return int(round(lam))
        return int(self.rng.poisson(lam))

    def lead_time(self, mu: float, sigma: float) -> float:
        if sigma <= 0:
            return max(0.0, mu)
        return max(0.0, float(self.rng.normal(mu, sigma)))
