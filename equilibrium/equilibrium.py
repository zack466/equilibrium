from operator import mul
from functools import reduce
import enum
import seaborn as sns
from matplotlib import pyplot as plt

prod = lambda x: reduce(mul, x, 1)


class ETYPE(enum.Enum):
    update_conc = 0  # assumes value = (name_of_element, change_in_conc)
    update_K = 1  # assumes value = lambda from K to new_K


class Event:
    def __init__(self, event_type, time, value, name=""):
        self.event_type = event_type
        self.time = time
        self.value = value
        if name == "":
            self.name = f"{event_type}, t={time}, {value}"
        else:
            self.name = name
        self.completed = False


class Reaction:
    def __init__(self, K=1, reactants=[], products=[], events=[]):
        self.min_end_time = 0
        self.dt = 0.03
        self.t = 0

        self.K = K
        assert K != 0, "K cannot be 0"

        self.reactants = reactants
        self.products = products

        self.events = []
        for event in events:
            self.events.append(event)
            self.min_end_time = max(self.min_end_time, event.time)

        self.times = [0]  # x-values for plotting
        self.Qhistory = [self.reaction_quotient(*self.rates())]
        self.Khistory = [self.K]

    def rates(self):
        # calculates forward and backwards rates
        # kf = K, kr = 1, so kf/kr = K
        forward = prod(map(lambda x: x.conc ** x.coeff, self.reactants)) * self.K
        backward = prod(map(lambda x: x.conc ** x.coeff, self.products))
        return forward, backward

    def react(self, forward, backward):
        # simulates a single reaction and updates state
        for r in self.reactants:
            r.conc -= self.dt * r.coeff * (forward - backward)
        for p in self.products:
            p.conc -= self.dt * p.coeff * (backward - forward)

        self.t += 1
        self.times.append(self.t)
        self.Qhistory.append(self.reaction_quotient(forward, backward))
        self.Khistory.append(self.K)

    def react_until_eq(self, threshold=0.001):
        # reacts until the net change in concentrations is less than threshold
        # will not stop reacting until all events have occurred
        while True:
            forward, backward = self.rates()
            if abs(forward - backward) < threshold and self.t > self.min_end_time:
                break
            else:
                self.do_events()
                self.react(*self.rates())

    def reaction_quotient(self, forward, backward):
        # calculates Q, the reaction quotient
        numer = backward
        denom = forward / self.K
        if denom == 0:  # prevent divide-by-zero errors
            denom += 1e-6
        return numer / denom

    def print_state(self):
        # for debugging
        print(f"{self.t}:")
        print("\tReactants:")
        for r in self.reactants:
            print("\t\t" + str(r))
        print("\tProducts:")
        for p in self.products:
            print("\t\t" + str(p))

    def do_events(self):
        i = 0
        # activates any events that should occur at this timestep
        while i < len(self.events):
            e = self.events[i]
            if e.time == self.t and not e.completed:
                self.do_event(e)
                e.completed = True
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
                    # to keep all concentration histories in sync
                    x.conc = x.conc
            self.times.append(self.t)
            self.Qhistory.append(self.reaction_quotient(*self.rates()))
            self.Khistory.append(self.K)
        elif t == ETYPE.update_K:
            val = event.value
            self.K = val(self.K)
        else:
            print(f"Event at {event.time} not found")

    def equation(self):
        # used to generate title of graph
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

    def plot(
        self,
        show_events=False,
        show_legend=True,
        show_reaction=False,
        show_title=True,
        plot_name="plot.png",
    ):
        elements = self.reactants + self.products
        line_colors = sns.color_palette("Set1", len(elements) + 2)
        for i, e in enumerate(elements):
            plt.plot(self.times, e.history, color=line_colors[i], label=e.name)

        if show_reaction:
            plt.plot(
                self.times,
                self.Qhistory,
                color=line_colors[-2],
                label="Q",
                linestyle="dashed",
            )
            plt.plot(
                self.times,
                self.Khistory,
                color=line_colors[-1],
                label="K",
                linestyle="dashed",
            )

        if show_events:
            event_colors = sns.color_palette("Set2", len(self.events))
            for i, e in enumerate(self.events):
                plt.axvline(
                    e.time, color=event_colors[i], label=e.name, linestyle="dashed"
                )

        if show_legend:
            plt.legend()

        if show_title:
            plt.title(self.equation())

        plt.xlabel("t")
        plt.ylabel("Concentration")

        plt.savefig(plot_name)


class Element:
    def __init__(self, name="", coeff=1, init_conc=1):
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
        # custom setter to keep track of history
        self.history.append(newconc)
        self._conc = newconc
