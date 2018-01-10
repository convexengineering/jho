import numpy as np
from numpy import pi
from gpkitmodels.GP.aircraft.mission.breguet_endurance import BreguetEndurance
from gpkitmodels.GP.aircraft.engine.df70 import DF70
from gpkitmodels.GP.aircraft.engine.gas_engine import Engine
from gpkitmodels.SP.aircraft.wing.wing import Wing
from gpkitmodels.GP.aircraft.fuselage.cylindrical_fuselage import Fuselage
from gpkitmodels.GP.aircraft.tail.empennage import Empennage
from gpkitmodels.GP.aircraft.tail.tail_boom import TailBoomState
from gpkitmodels.SP.aircraft.tail.tail_boom_flex import TailBoomFlexibility
from helpers import summing_vars
from gpkit import Model, Variable, Vectorize, units
from gpkit.tools.autosweep import autosweep_1d
import matplotlib.pyplot as plt

# pylint: disable=invalid-name

class Aircraft(Model):
    "the JHO vehicle"
    def setup(self, Wfueltot, df70=True):

        self.fuselage = Fuselage(Wfueltot)
        self.wing = Wing(N=14)
        if df70:
            self.engine = DF70()
        else:
            self.engine = Engine()
        self.emp = Empennage()
        self.pylon = Pylon()

        components = [self.fuselage, self.wing, self.engine, self.emp,
                      self.pylon]
        self.smeared_loads = [self.fuselage, self.engine, self.pylon]
        # components = [self.fuselage, self.wing, self.engine, self.emp]
        # self.smeared_loads = [self.fuselage, self.engine]

        Wzfw = Variable("W_{zfw}", "lbf", "zero fuel weight")
        Wpay = Variable("W_{pay}", 10, "lbf", "payload weight")
        Ppay = Variable("P_{pay}", 10, "W", "payload power")
        Wavn = Variable("W_{avn}", 5.35, "lbf", "avionics weight")
        lantenna = Variable("l_{antenna}", 13.4, "in", "antenna length")
        wantenna = Variable("w_{antenna}", 10.2, "in", "antenna width")
        # propr = Variable("r", 11, "in", "propellor radius")
        Volpay = Variable("\\mathcal{V}_{pay}", 1.0, "ft**3", "payload volume")
        Volavn = Variable("\\mathcal{V}_{avn}", 0.125, "ft**3",
                          "avionics volume")

        constraints = [
            Wzfw >= sum(summing_vars(components, "W")) + Wpay + Wavn,
            self.emp.htail.Vh <= (
                self.emp.htail["S"]
                * self.emp.htail.lh/self.wing["S"]**2
                * self.wing["b"]),
            self.emp.vtail.Vv == (
                self.emp.vtail["S"]
                * self.emp.vtail.lv/self.wing["S"]
                / self.wing["b"]),
            self.wing.planform.CLmax/self.wing.mw <= (
                self.emp.htail.planform.CLmax
                / self.emp.htail.mh),
            # enforce antenna sticking on the tail
            self.emp.vtail.planform.croot*self.emp.vtail.planform.lam >= (
                wantenna),
            self.emp.vtail["b"] >= lantenna,
            # enforce a cruciform with the htail infront of vertical tail
            self.emp.tailboom["l"] >= (
                self.emp.htail.lh
                + self.emp.htail.planform.croot),
            4./6*pi*self.fuselage["k_{nose}"]*self.fuselage["R"]**3 >= Volpay,
            self.fuselage["\\mathcal{V}_{body}"] >= (
                self.fuselage.fueltank["\\mathcal{V}"] + Volavn),
            ]

        if df70:
            constraints.extend([self.engine["h"] <= 2*self.fuselage["R"]])

        return components, constraints

    def flight_model(self, state):
        return AircraftPerf(self, state)

    def loading(self, Wcent):
        return AircraftLoading(self, Wcent)

class Pylon(Model):
    "attachment from fuselage to pylon"
    def setup(self):

        h = Variable("h", 7, "in", "pylon height")
        l = Variable("l", 32.8, "in", "pylon length")
        S = Variable("S", "ft**2", "pylon surface area")
        W = Variable("W", 1.83, "lbf", "pylon weight")

        constraints = [S >= 2*l*h]

        return constraints

    def flight_model(self, state):
        return PylonAero(self, state)

class PylonAero(Model):
    "pylon drag model"
    def setup(self, static, state):

        Cf = Variable("C_f", "-", "fuselage skin friction coefficient")
        Re = Variable("Re", "-", "fuselage reynolds number")

        constraints = [
            Re == state["V"]*state["\\rho"]*static["l"]/state["\\mu"],
            Cf >= 0.455/Re**0.3,
            ]

        return constraints

class AircraftLoading(Model):
    "aircraft loading model"
    def setup(self, aircraft, Wcent):

        loading = []
        loading.append(aircraft.fuselage.loading(Wcent))

        loading.append(TailBoomFlexibility(aircraft.emp.htail,
                                           aircraft.emp.hbend,
                                           aircraft.wing))

        return loading

class AircraftPerf(Model):
    "performance model for aircraft"
    def setup(self, static, state, **kwargs):

        self.wing = static.wing.flight_model(static.wing, state)
        self.fuselage = static.fuselage.flight_model(state)
        self.engine = static.engine.flight_model(state)
        self.htail = static.emp.htail.flight_model(static.emp.htail, state)
        self.vtail = static.emp.vtail.flight_model(static.emp.vtail, state)
        self.tailboom = static.emp.tailboom.flight_model(static.emp.tailboom,
                                                         state)
        self.pylon = static.pylon.flight_model(state)

        self.dynamicmodels = [self.wing, self.fuselage, self.engine,
                              self.htail, self.vtail, self.tailboom, self.pylon]
        areadragmodel = [self.fuselage, self.htail, self.vtail, self.tailboom,
                         self.pylon]
        areadragcomps = [static.fuselage, static.emp.htail,
                         static.emp.vtail,
                         static.emp.tailboom, static.pylon]

        Wend = Variable("W_{end}", "lbf", "vector-end weight")
        Wstart = Variable("W_{start}", "lbf", "vector-begin weight")
        CD = Variable("C_D", "-", "drag coefficient")
        CDA = Variable("CDA", "-", "area drag coefficient")
        mfac = Variable("m_{fac}", 1.15, "-", "drag margin factor")

        dvars = []
        for dc, dm in zip(areadragcomps, areadragmodel):
            if "C_d" in dm.varkeys:
                dvars.append(dm["C_d"]*dc["S"]/static.wing["S"])
            if "Cd" in dm.varkeys:
                dvars.append(dm["Cd"]*dc["S"]/static.wing["S"])
            if "Cf" in dm.varkeys:
                dvars.append(dm["Cf"]*dc["S"]/static.wing["S"])
            if "C_f" in dm.varkeys:
                dvars.append(dm["C_f"]*dc["S"]/static.wing["S"])

        constraints = [CDA >= sum(dvars),
                       CD/mfac >= CDA + self.wing.Cd]

        return self.dynamicmodels, constraints

class FlightState(Model):
    "define environment state during a portion of an aircraft mission"
    def setup(self, alt, wind, **kwargs):

        rho = self.rho = Variable("\\rho", "kg/m^3", "air density")
        h = Variable("h", alt, "ft", "altitude")
        href = Variable("h_{ref}", 15000, "ft", "Reference altitude")
        psl = Variable("p_{sl}", 101325, "Pa", "Pressure at sea level")
        Latm = Variable("L_{atm}", 0.0065, "K/m", "Temperature lapse rate")
        Tsl = Variable("T_{sl}", 288.15, "K", "Temperature at sea level")
        temp = [(t.value - l.value*v.value).magnitude
                for t, v, l in zip(Tsl, h, Latm)]
        Tatm = Variable("t_{atm}", temp, "K", "Air temperature")
        mu = self.mu = Variable("\\mu", "N*s/m^2", "Dynamic viscosity")
        musl = Variable("\\mu_{sl}", 1.789*10**-5, "N*s/m^2",
                        "Dynamic viscosity at sea level")
        Rspec = Variable("R_{spec}", 287.058, "J/kg/K",
                         "Specific gas constant of air")

        # Atmospheric variation with altitude (valid from 0-7km of altitude)
        constraints = [rho == psl*Tatm**(5.257-1)/Rspec/(Tsl**5.257),
                       (mu/musl)**0.1 == 0.991*(h/href)**(-0.00529),
                       Latm == Latm]

        V = self.V = Variable("V", "m/s", "true airspeed")
        mfac = Variable("m_{fac}", 1.0, "-", "wind speed margin factor")

        if wind:

            V_wind = Variable("V_{wind}", 25, "m/s", "Wind speed")
            constraints.extend([V/mfac >= V_wind])

        else:

            V_wind = Variable("V_{wind}", "m/s", "Wind speed")
            V_ref = Variable("V_{ref}", 25, "m/s", "Reference wind speed")

            constraints.extend([(V_wind/V_ref) >= 0.6462*(h/href) + 0.3538,
                                V/mfac >= V_wind])
        return constraints

class FlightSegment(Model):
    "creates flight segment for aircraft"
    def setup(self, N, aircraft, alt=15000, wind=False, etap=0.7):

        self.aircraft = aircraft

        with Vectorize(N):
            self.fs = FlightState(alt, wind)
            self.aircraftPerf = self.aircraft.flight_model(self.fs)
            self.slf = SteadyLevelFlight(self.fs, self.aircraft,
                                         self.aircraftPerf, etap)
            self.be = BreguetEndurance(self.aircraftPerf)

        self.submodels = [self.fs, self.aircraftPerf, self.slf, self.be]

        Wfuelfs = Variable("W_{fuel-fs}", "lbf", "flight segment fuel weight")

        self.constraints = [Wfuelfs >= self.be["W_{fuel}"].sum()]

        if N > 1:
            self.constraints.extend([self.aircraftPerf["W_{end}"][:-1] >=
                                     self.aircraftPerf["W_{start}"][1:]])

        return self.aircraft, self.submodels, self.constraints

class Loiter(Model):
    "make a loiter flight segment"
    def setup(self, N, aircraft, alt=15000, wind=False, etap=0.7):
        fs = FlightSegment(N, aircraft, alt, wind, etap)

        t = Variable("t", "days", "time loitering")
        constraints = [fs.be["t"] >= t/N]

        return constraints, fs

class Cruise(Model):
    "make a cruise flight segment"
    def setup(self, N, aircraft, alt=15000, wind=False, etap=0.7, R=200):
        fs = FlightSegment(N, aircraft, alt, wind, etap)

        R = Variable("R", R, "nautical_miles", "Range to station")
        constraints = [R/N <= fs["V"]*fs.be["t"]]

        return fs, constraints

class Climb(Model):
    "make a climb flight segment"
    def setup(self, N, aircraft, alt=15000, wind=False, etap=0.7, dh=15000):
        fs = FlightSegment(N, aircraft, alt, wind, etap)

        with Vectorize(N):
            hdot = Variable("\\dot{h}", "ft/min", "Climb rate")

        deltah = Variable("\\Delta h", dh, "ft", "altitude difference")
        hdotmin = Variable("\\dot{h}_{min}", 100, "ft/min",
                           "minimum climb rate")

        constraints = [
            hdot*fs.be["t"] >= deltah/N,
            hdot >= hdotmin,
            fs.slf["T"] >= (0.5*fs["\\rho"]*fs["V"]**2*fs["C_D"]
                            * fs.aircraft.wing["S"] + fs["W_{start}"]*hdot
                            / fs["V"]),
            ]

        return fs, constraints

class SLFMaxSpeed(Model):
    "steady level flight model"
    def setup(self, state, aircraft, perf, etap):

        T = Variable("T", "N", "thrust")
        etaprop = Variable("\\eta_{prop}", etap, "-", "propulsive efficiency")

        constraints = [
            (perf["W_{end}"]*perf["W_{start}"])**0.5 <= (
                0.5*state["\\rho"]*state["V_{max}"]**2*perf.wing.CL
                * aircraft.wing["S"]),
            T >= (0.5*state["\\rho"]*state["V_{max}"]**2*perf["C_D"]
                  *aircraft.wing["S"]),
            perf["P_{shaft-max}"] >= T*state["V_{max}"]/etaprop]

        return constraints

class SteadyLevelFlight(Model):
    "steady level flight model"
    def setup(self, state, aircraft, perf, etap):

        T = Variable("T", "N", "thrust")
        etaprop = Variable("\\eta_{prop}", etap, "-", "propulsive efficiency")

        constraints = [
            (perf["W_{end}"]*perf["W_{start}"])**0.5 <= (
                0.5*state["\\rho"]*state["V"]**2*perf.wing.CL
                * aircraft.wing["S"]),
            T >= (0.5*state["\\rho"]*state["V"]**2*perf["C_D"]
                  *aircraft.wing["S"]),
            perf["P_{shaft}"] >= T*state["V"]/etaprop]

        return constraints

class Mission(Model):
    "creates flight profile"
    def setup(self, wind=False, DF70=True):

        mtow = Variable("MTOW", "lbf", "max-take off weight")
        Wcent = Variable("W_{cent}", "lbf", "center aircraft weight")
        Wfueltot = Variable("W_{fuel-tot}", "lbf", "total aircraft fuel weight")

        self.JHO = Aircraft(Wfueltot, df70=DF70)
        loading = self.JHO.loading(Wcent)
        wingl = self.JHO.wing.spar.loading(self.JHO.wing)

        LS = Variable("(W/S)", "lbf/ft**2", "wing loading",
                      evalfn=lambda v: v[mtow]/v[self.JHO.wing.planform["S"]])

        climb1 = Climb(10, self.JHO, alt=np.linspace(0, 15000, 11)[1:], etap=0.508, wind=wind)
        cruise1 = Cruise(1, self.JHO, etap=0.684, R=180, wind=wind)
        loiter1 = Loiter(5, self.JHO, etap=0.647, wind=wind)
        cruise2 = Cruise(1, self.JHO, etap=0.684, wind=wind)
        mission = [climb1, cruise1, loiter1, cruise2]

        constraints = [
            mtow == climb1["W_{start}"][0],
            Wfueltot >= sum(fs["W_{fuel-fs}"] for fs in mission),
            mission[-1]["W_{end}"][-1] >= self.JHO["W_{zfw}"],
            Wcent >= Wfueltot + sum(summing_vars(self.JHO.smeared_loads, "W")),
            loiter1["P_{total}"] >= (loiter1["P_{shaft}"] + (
                loiter1["P_{avn}"] + self.JHO["P_{pay}"])
                                     / loiter1["\\eta_{alternator}"]),
            Wcent == wingl["W"]
            ]

        for i, fs in enumerate(mission[1:]):
            constraints.extend([
                mission[i]["W_{end}"][-1] == fs["W_{start}"][0]
                ])

        return self.JHO, mission, loading, constraints, wingl

def test():
    "test method run by external CI"
    model = Mission()
    model.substitutions[model.JHO.emp.vtail.Vv] = 0.04
    model.cost = 1/model["t_Mission/Loiter"]
    model.localsolve("mosek")

if __name__ == "__main__":
    M = Mission(DF70=True)
    M.substitutions[M.JHO.emp.vtail.Vv] = 0.04
    M.cost = 1/M["t_Mission/Loiter"]
    sol = M.localsolve("mosek")

    # M = Mission(DF70=False)
    # M.cost = 1/M["t_Mission/Loiter"]
    # lower = 50
    # upper = 1000
    # xmin_ = np.linspace(lower, upper, 100)
    # bst = autosweep_1d(M, 1e-2, M["MTOW"], [lower, upper], solver="mosek")

    # fig, ax = plt.subplots()
    # ax.plot(xmin_, 1/bst.sample_at(xmin_)["cost"])
    # ax.set_xlabel("Max Take Off Weight [lbf]")
    # ax.set_ylabel("Endurance [days]")
    # ax.grid()
    # fig.savefig("mtowtend.pdf")


