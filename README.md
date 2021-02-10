# Equilibrium

Simulate equilibrium and generate plots! A working example is located in `main.py`.

## Steps to Use
1. Initialize a `Reaction` with values for `kf` and `kr`
2. Initialize `Element` objects with a coefficient and initial concentration.
Add these to the reaction using the `add_reactant` and `add_product` methods.
3. Initialize `Event` objects if you wish to change an element's concentration, `kf`, or `kr` during the reaction.
Add these to the reaction using `add_event`.
4. Run the simulation using the `react_until_eq` method.
5. Plot the reaction using the plot function, which requires the product/reactant objects, the reaction object, and the events objects.

## Example Plot
![Plot](plot.png)
