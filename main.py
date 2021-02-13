import equilibrium as eq

# Reaction config
A = eq.Element(name="A", coeff=1, init_conc=0.5)
B = eq.Element(name="B", coeff=2, init_conc=0.75)
C = eq.Element(name="C", coeff=1, init_conc=0)
X = eq.Event(eq.ETYPE.update_conc, 30, ("C", 0.2), name="add C")

# run experiment
R = eq.Reaction(K=1.2, reactants=[A, B], products=[C], events=[X])
R.react_until_eq(threshold=0.001)

# plotting
R.plot(show_events=True)
