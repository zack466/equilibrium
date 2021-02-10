import equilibrium as eq

# config
R = eq.Reaction(kf=0.5, kr=1)

A = eq.Element("A", 1, 0.5)
B = eq.Element("B", 2, 1)
R.add_reactant(A)
R.add_reactant(B)

C = eq.Element("C", 2, 0)
R.add_product(C)

x = eq.Event(eq.ETYPE.update_conc, 20, ("B", 0.14), name="add_A")
R.add_event(x)

# run experiment
R.react_until_eq(threshold=0.001)

# plotting
elements = [A, B, C]
eq.plot(elements, R, [x], show_events=True)

# plt.show()
