from core.optimizers import PulpFeedOptimizer

def run_optimization(ingredients, constraints):
    return PulpFeedOptimizer().optimize(ingredients, constraints)
