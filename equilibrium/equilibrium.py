from operator import mul
from functools import reduce
import enum
import seaborn as sns
from matplotlib import pyplot as plt
from copy import deepcopy

prod = lambda x: reduce(mul, x, 1)

class ETYPE(enum.Enum):
    update_conc = 0
    update_kf = 1
    update_kr = 2

class Event():
    def __init__(self, event_type, time, value, name=""):
        self.event_type = event_type
        self.time = time
        self.value = value
        self.name = name

class Reaction():
    def __init__(self, kf=1, kr=1):
        self.reactants = []
        self.products = []
        self.events = []
        self.min_end_time = 0
        self.dt = 0.05
        self.t = 0
        self.kf = kf # forward rate constnat
        self.kr = kr # reverse rate constant
        self.times = [0]
        self.Qhistory = [self.reaction_quotient()]
        self.Khistory = [self.K()]

    def rates(self):
        forward = prod(map(lambda x: x.conc ** x.coeff, self.reactants)) * self.kf
        backward = prod(map(lambda x: x.conc ** x.coeff, self.products)) * self.kr
        return forward, backward

    def react(self):
        if self.t == 0:
            self.Qhistory = [self.reaction_quotient()]
        self.do_events()
        forward, backward = self.rates()
        for r in self.reactants:
            r.conc -= self.dt * r.coeff * (forward - backward)
        for p in self.products:
            p.conc -= self.dt * p.coeff * (backward - forward)
        self.t += 1
        self.times.append(self.t)
        self.Qhistory.append(self.reaction_quotient())
        self.Khistory.append(self.K())

    def react_until_eq(self, threshold=0.005):
        while True:
            forward, backward = self.rates()
            if abs(forward - backward) < threshold and self.t > self.min_end_time:
                break
            else:
                self.react()

    def reaction_quotient(self):
        forward, backward = self.rates()
        numer = backward / self.kr
        denom = forward / self.kf
        if denom == 0:
            denom += 1e-6
        return numer / denom
    
    def K(self):
        return self.kf / self.kr

    def print_state(self):
        print(f"{self.t}:")
        print("\tReactants:")
        for r in self.reactants:
            print("\t\t" + str(r))
        print("\tProducts:")
        for p in self.products:
            print("\t\t" + str(p))

    def add_reactant(self, r):
        self.reactants.append(r)

    def add_product(self, p):
        self.products.append(p)

    def add_event(self, event):
        self.events.append(event)
        self.min_end_time = max(self.min_end_time, event.time)

    def add_events(self, event_list):
        for event in event_list:
            self.add_event(event)

    def do_events(self):
        i = 0
        while i < len(self.events):
            e = self.events[i]
            if e.time == self.t:
                self.do_event(e)
                self.events.pop(i)
                i = 0
            else:
                i += 1

    def do_event(self, event):
        t = event.event_type 
        if t == ETYPE.update_conc:
            name, val = event.value
            for x in self.products + self.reactants:
                if x.name == name:
                    x.conc += val
                else:
                    x.conc = x.conc
            self.times.append(self.t)
            self.Qhistory.append(self.reaction_quotient())
            self.Khistory.append(self.K())
        elif t == ETYPE.update_kf:
            val = event.value
            self.kf += val
        elif t == ETYPE.update_kr:
            val = event.value
            self.kr += val
        else:
            print(f"Event at {event.time} not found")

    def equation(self):
        strs = []
        for i in range(len(self.reactants)):
            r = self.reactants[i]
            strs.append(f"{r.coeff}{r.name}")
            if i < len(self.reactants) - 1:
                strs.append(" + ")
        strs.append(" <=> ")
        for i in range(len(self.products)):
            p = self.products[i]
            strs.append(f"{p.coeff}{p.name}")
            if i < len(self.products) - 1:
                strs.append(" + ")
        return "".join(strs)

class Element():
    def __init__(self, name, coeff, init_conc):
        self.name = name
        self._conc = init_conc
        self.coeff = coeff
        self.history = [init_conc]

    def __repr__(self):
        return f"{self.name}_{self.coeff}: {self.conc}"
    
    @property
    def conc(self):
        return self._conc

    @conc.setter
    def conc(self, newconc):
        self.history.append(newconc)
        self._conc = newconc

def plot(elements, reaction, events=[], show_events=False, show_legend=True, show_reaction=False, show_title=True):
    R = reaction
    line_colors = sns.color_palette("Set1", len(elements) + 2)
    for i, e in enumerate(elements):
        plt.plot(R.times, e.history, color=line_colors[i], label=e.name)
    
    if show_reaction:
        plt.plot(R.times, R.Qhistory, color=line_colors[-2], label="Q", linestyle="dashed")
        plt.plot(R.times, R.Khistory, color=line_colors[-1], label="K", linestyle="dashed")
    
    if show_events:
        event_colors = sns.color_palette("Set2", len(events))
        for i, e in enumerate(events):
            plt.vlines(e.time, 0, 1, color=event_colors[i], label=e.name, linestyle="dashed")

    if show_legend:
        plt.legend()
    
    if show_title:
        plt.title(R.equation())

    plt.savefig("plot.png")