"""
Pytest configuration for PAYMENTIQ test suite.
Configures headless Matplotlib backend to avoid Tkinter GUI initialization.
"""
import matplotlib
matplotlib.use("Agg")
