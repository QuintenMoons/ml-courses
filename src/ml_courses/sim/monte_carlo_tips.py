"""
Monte Carlo simulation for coffee shop tips example.

This module provides a Monte Carlo simulation for estimating linear regression parameters
in the coffee shop tips example using a naive sampling approach.
"""

from typing import TypedDict

import numpy as np


class SimulationResults(TypedDict):
    """TypedDict for Monte Carlo simulation results."""

    final_b1: float
    final_b2: float
    final_loss: float
    acceptance_rate: float
    b1_samples: list[float]
    b2_samples: list[float]
    loss_samples: list[float]


class MonteCarloTipsSimulation:
    """
    Simulation class for coffee shop tips analysis.

    Monte Carlo simulation for estimating linear regression parameters (b1, b2)
    in the coffee shop tips example using a naive sampling approach.

    This class generates synthetic data based on true parameters and runs
    a Monte Carlo optimization to minimize the Sum of Squared Errors (SSE) loss.
    """

    def __init__(  # noqa: PLR0913
        self,
        n_customers: int = 50,
        true_b1: float = 0.50,
        true_b2: float = 0.15,
        noise_std: float = 0.30,
        order_min: float = 3,
        order_max: float = 25,
        seed: int = 42,
    ) -> None:
        """
        Initialize the simulation with data generation parameters.

        Parameters
        ----------
        n_customers : int
            Number of customer data points to generate.
        true_b1 : float
            True base tip amount.
        true_b2 : float
            True tip rate (multiplier for order total).
        noise_std : float
            Standard deviation of noise in tip observations.
        order_min : float
            Minimum order total.
        order_max : float
            Maximum order total.
        seed : int
            Random seed for reproducibility.
        """
        self.n_customers = n_customers
        self.true_b1 = true_b1
        self.true_b2 = true_b2
        self.noise_std = noise_std
        self.order_min = order_min
        self.order_max = order_max
        self.rng = np.random.default_rng(seed)
        self.generate_data()

    def generate_data(self) -> None:
        """Generate synthetic order totals and observed tips based on true parameters."""
        self.order_totals = self.rng.uniform(self.order_min, self.order_max, self.n_customers)
        self.order_totals = np.sort(self.order_totals)  # Sort for nicer visualization
        self.true_tips = self.true_b1 + self.true_b2 * self.order_totals
        noise = self.rng.normal(0, self.noise_std, self.n_customers)
        self.observed_tips = np.maximum(0, self.true_tips + noise)  # Tips can't be negative

    @staticmethod
    def calculate_loss(b1: float, b2: float, x: np.ndarray, y: np.ndarray) -> float:
        """
        Calculate the Sum of Squared Errors (SSE) loss.

        Parameters
        ----------
        b1 : float
            Base tip amount.
        b2 : float
            Tip rate.
        x : array-like
            Order totals.
        y : array-like
            Observed tips.

        Returns
        -------
        float
            SSE loss value.
        """
        y_hat = b1 + b2 * x
        d = y - y_hat
        return np.sum(d**2)

    def run_simulation(  # noqa: PLR0913
        self,
        n_samples: int = 30000,
        step_size: float = 0.0001,
        b1_init: float | None = None,
        b2_init: float | None = None,
        b1_bounds: tuple[float, float] = (0, 50),
        b2_bounds: tuple[float, float] = (0, 1.0),
        order_totals: np.ndarray | None = None,
        observed_tips: np.ndarray | None = None,
    ) -> SimulationResults:
        """
        Run the Monte Carlo simulation to estimate b1 and b2.

        Parameters
        ----------
        n_samples : int
            Number of Monte Carlo samples.
        step_size : float
            Step size for parameter proposals.
        b1_init : float, optional
            Initial guess for b1. If None, random uniform [0, 10].
        b2_init : float, optional
            Initial guess for b2. If None, random uniform [0.05, 0.50].
        b1_bounds : tuple
            Bounds for b1 (min, max).
        b2_bounds : tuple
            Bounds for b2 (min, max).
        order_totals : array-like, optional
            Order totals to use. If None, uses internally generated data.
        observed_tips : array-like, optional
            Observed tips to use. If None, uses internally generated data.

        Returns
        -------
        SimulationResults
            Results containing final parameters, loss, acceptance rate, and sample histories.
        """
        if b1_init is None:
            b1_init = self.rng.uniform(0, 10)
        if b2_init is None:
            b2_init = self.rng.uniform(0.05, 0.50)

        if order_totals is None:
            order_totals = self.order_totals
        if observed_tips is None:
            observed_tips = self.observed_tips

        b1 = b1_init
        b2 = b2_init
        current_loss = self.calculate_loss(b1, b2, order_totals, observed_tips)

        b1_samples = [b1]
        b2_samples = [b2]
        loss_samples = [current_loss]

        n_accepted = 0

        for _ in range(n_samples):
            b1_new = b1 + self.rng.normal(0, step_size * 5)  # Base tip can vary more
            b2_new = b2 + self.rng.normal(0, step_size)

            b1_new = np.clip(b1_new, *b1_bounds)
            b2_new = np.clip(b2_new, *b2_bounds)

            new_loss = self.calculate_loss(b1_new, b2_new, order_totals, observed_tips)

            if new_loss < current_loss:
                b1 = b1_new
                b2 = b2_new
                current_loss = new_loss
                n_accepted += 1

            b1_samples.append(b1)
            b2_samples.append(b2)
            loss_samples.append(current_loss)

        acceptance_rate = n_accepted / n_samples

        return {
            "final_b1": b1,
            "final_b2": b2,
            "final_loss": current_loss,
            "acceptance_rate": acceptance_rate,
            "b1_samples": b1_samples,
            "b2_samples": b2_samples,
            "loss_samples": loss_samples,
        }
