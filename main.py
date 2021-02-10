import equilibrium.equilibrium as eq

# Reaction config
R = eq.Reaction(kf=0.8, kr=1.2)

A = eq.Element(name="A", coeff=1, init_conc=0.5)
B = eq.Element(name="B", coeff=2, init_conc=1)
R.add_reactants([A, B])

C = eq.Element(name="C", coeff=2, init_conc=0)
R.add_product(C)

x = eq.Event(eq.ETYPE.update_conc, 20, ("C", 0.25), name="add_A")
R.add_event(x)

# run experiment
R.react_until_eq(threshold=0.001)

# plotting
elements = [A, B, C]
eq.plot(elements, R, [x], show_events=True)

# plt.show()
