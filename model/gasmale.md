# GAS-POWERED, MEDIUM-ALTITUDE, LONG-ENDURANCE AIRCRAFT

This paper presents the designs achieved in the 82 project. This also presents all of the models used in the design of this aircraft.

## Aircraft Model
\input{tex/Aircraft.vars.generated.tex}
\input{tex/Aircraft.cnstrs.generated.tex}

## Climb Model
\input{tex/Climb.vars.generated.tex}
\input{tex/Climb.cnstrs.generated.tex}

## Cruise Model
\input{tex/Cruise.vars.generated.tex}
\input{tex/cnstrs.generated.tex}

## Loiter Model
\input{tex/Loiter.vars.generated.tex}
\input{tex/Loiter.cnstrs.generated.tex}

## AircraftLoading Model
\input{tex/AircraftLoading.vars.generated.tex}
\input{tex/AircraftLoading.cnstrs.generated.tex}

## Fuselage Model
\input{tex/Fuselage.vars.generated.tex}
\input{tex/Fuselage.cnstrs.generated.tex}

## Wing Model
\input{tex/Wing.vars.generated.tex}
\input{tex/Wing.cnstrs.generated.tex}

## Engine Model
\input{tex/Engine.vars.generated.tex}
\input{tex/Engine.cnstrs.generated.tex}

## Empennage Model
\input{tex/Empennage.vars.generated.tex}
\input{tex/Empennage.cnstrs.generated.tex}

## Flight Segment Model
\input{tex/FlightSegment.vars.generated.tex}
\input{tex/FlightSegment.cnstrs.generated.tex}

## Wing Loading Model
\input{tex/WingLoading.vars.generated.tex}
\input{tex/WingLoading.cnstrs.generated.tex}

## Empennage Loading Model
\input{tex/EmpennageLoading.vars.generated.tex}
\input{tex/EmpennageLoading.cnstrs.generated.tex}

## Fuselage Loading Model
\input{tex/FuselageLoading.vars.generated.tex}
\input{tex/FuselageLoading.cnstrs.generated.tex}

## Fuel Tank Model
\input{tex/FuelTank.vars.generated.tex}
\input{tex/FuelTank.cnstrs.generated.tex}

## Fuselage Skin Model
\input{tex/FuselageSkin.vars.generated.tex}
\input{tex/FuselageSkin.cnstrs.generated.tex}

## Cap Spar Model
\input{tex/CapSpar.vars.generated.tex}
\input{tex/CapSpar.cnstrs.generated.tex}

## Wing Skin Model
\input{tex/WingSkin.vars.generated.tex}
\input{tex/WingSkin.cnstrs.generated.tex}

## Wing Interior Model
\input{tex/WingInterior.vars.generated.tex}
\input{tex/WingInterior.cnstrs.generated.tex}

## Horizontal Tail Model
\input{tex/HorizontalTail.vars.generated.tex}
\input{tex/HorizontalTail.cnstrs.generated.tex}

## Vertical Tail Model
\input{tex/VerticalTail.vars.generated.tex}
\input{tex/VerticalTail.cnstrs.generated.tex}

## Tail Boom Model
\input{tex/TailBoom.vars.generated.tex}
\input{tex/TailBoom.cnstrs.generated.tex}

## Flight State Model
\input{tex/FlightState.vars.generated.tex}
\input{tex/FlightState.cnstrs.generated.tex}

## Aircraft Performance Model
\input{tex/AircraftPerf.vars.generated.tex}
\input{tex/AircraftPerf.cnstrs.generated.tex}

## Steady Level Flight Model
\input{tex/SteadyLevelFlight.vars.generated.tex}
\input{tex/SteadyLevelFlight.cnstrs.generated.tex}

## Breguet Endurance Model
\input{tex/BreguetEndurance.vars.generated.tex}
\input{tex/BreguetEndurance.cnstrs.generated.tex}

## Wing Skin Loading Model
\input{tex/WingSkinL.vars.generated.tex}
\input{tex/WingSkinL.cnstrs.generated.tex}

## Chord Spar Loading
\input{tex/ChordSparL.vars.generated.tex}
\input{tex/ChordSparL.cnstrs.generated.tex}

## Horizontal Boom Bending
\input{tex/HorizontalBoomBending.vars.generated.tex}
\input{tex/HorizontalBoomBending.cnstrs.generated.tex}

## Vertical Boom Bending
\input{tex/VerticalBoomBending.vars.generated.tex}
\input{tex/VerticalBoomBending.cnstrs.generated.tex}

## Vertical Boom Torsion
\input{tex/VerticalBoomTorsion.vars.generated.tex}
\input{tex/VerticalBoomTorsion.cnstrs.generated.tex}

## Fuselage Skin Loading Model
\input{tex/FuselageSkinL.vars.generated.tex}
\input{tex/FuselageSkinL.cnstrs.generated.tex}

## Wing Areodynamics Model
\input{tex/WingAero.vars.generated.tex}
\input{tex/WingAero.cnstrs.generated.tex}

## Fuselage Areodynamics Model
\input{tex/FuselageAero.vars.generated.tex}
\input{tex/FuselageAero.cnstrs.generated.tex}

## Engine Performance Model
\input{tex/EnginePerf.vars.generated.tex}
\input{tex/EnginePerf.cnstrs.generated.tex}

## HorizontalTail Areodynamics Model
\input{tex/HorizontalTailAero.vars.generated.tex}
\input{tex/HorizontalTailAero.cnstrs.generated.tex}

## VerticalTail Areodynamics Model
\input{tex/VerticalTailAero.vars.generated.tex}
\input{tex/VerticalTailAero.cnstrs.generated.tex}

## TailBoom Areodynamics Model
\input{tex/TailBoomAero.vars.generated.tex}
\input{tex/TailBoomAero.cnstrs.generated.tex}

## Beam Model
\input{tex/Beam.vars.generated.tex}
\input{tex/Beam.cnstrs.generated.tex}

## Mission Profile Model
\input{tex/Mission.vars.generated.tex}
\input{tex/Mission.cnstrs.generated.tex}

```python
#inPDF: skip
from gasmaleperf import Mission
from gen_tex import gen_model_tex, find_submodels, gen_tex_fig, gen_fixvars_tex 

M = Mission()
models, modelnames = find_submodels([M], [M.__class__.__name__])
for m in models: 
    print type(m)
    gen_model_tex(m, m.__class__.__name__)

```

# Sizing

This model was created and then a sweep was done to determine the MTOW required to meet 5 days. 

```python
#inPDF: replace with tex/tstation_vs_MTOW_rubber.fig.generated.tex
from plotting import plot_sweep, fix_vars, plot_altitude_sweeps
import numpy as np

M.substitutions.update({"MTOW": 150})
fig, ax = plot_sweep(M, "MTOW", np.linspace(70, 500, 15), ["t_Mission, Loiter"])
# gen_tex_fig(fig, "tstation_vs_MTOW_rubber")
fig.savefig("tstation_vs_MTOW_rubber")
```

### CDR Aircraft Sizing

After deciding on the 150 lb aircraft to meet with a 1 day margin on the loiter requirement, a DF70 engine was chosen. The aircraft was reoptimized to meet the 6 day time on station and minimize max take off weight.  This was the aircraft chosen for the CDR. The solution is shown in the tables below. 

```python
#inPDF: replace with tex/sol.generated.tex
M = Mission(DF70=True)
M.substitutions.update({"t_Mission, Loiter": 6})
M.cost = M["MTOW"]
sol = M.solve("mosek")

with open("tex/sol.generated.tex", "w") as f:
    f.write(sol.table(latex=True))
```

By fixing the following variables to their respective values we were also able to generate performance curves. 

```python
#inPDF: replace with tex/fixvars.table.generated.tex

vars_to_fix = {"b": 24, "l_Mission, Aircraft, Empennage, TailBoom": 7.0,
               "AR_v": 1.5, "AR": 24, "SM_{corr}": 0.5, "AR_h": 4}
gen_fixvars_tex(M, sol, vars_to_fix)
for p in M.varkeys["P_{avn}"]:
    M.substitutions.update({p: 65})

fix_vars(M, sol, vars_to_fix)
sol = M.solve("mosek") # check for solving errors
```

## Sweeps

```python
#inPDF: skip
# set objective to time on station after fixing variables
M.substitutions.update({"P_{pay}": 100})
# payload power vs time on station
fig, ax = plot_sweep(M, "P_{pay}", np.linspace(10, 200, 15), ["t_Mission, Loiter"], ylim=[0,10])
gen_tex_fig(fig, "t_vs_Ppay")

# payload weight vs time on station
fig, ax = plot_sweep(M, "W_{pay}", np.linspace(5, 20, 15), ["t_Mission, Loiter"], ylim=[0,10])
gen_tex_fig(fig, "t_vs_Wpay")

# wind speed vs time on station
M = Mission(wind=True, DF70=True)
fix_vars(M, sol, vars_to_fix)
M.substitutions.update({"P_{pay}": 100})
fig, ax = plot_sweep(M, "V_{wind}_Mision, Loiter, FlightSegment, FlightState", np.linspace(5, 40, 15), ["t_Mission, Loiter"], ylim=[0,10])
gen_tex_fig(fig, "t_vs_Vwind")

# altitude vs time on loiter
# altitude_vars = {"t_Mission, Loiter"}
# figs, axs = plot_altitude_sweeps(np.linspace(14000, 20000, 10), altitude_vars,
#                      vars_to_fix)
# axs[0].set_ylim([0,10])
# 
# for var, fig in zip(altitude_vars, figs):
#     gen_tex_fig(fig, "%s_vs_altitude" % var.replace("{", "").replace("}", "").replace("_", ""))
```
\input{tex/t_vs_Ppay.fig.generated.tex}
\input{tex/t_vs_Wpay.fig.generated.tex}
\input{tex/t_vs_Vwind.fig.generated.tex}

## Flight Profile

By further discretizing the climb, cruise, and loiter mission segments the following figures were generated to follow the performance over the duration of the mission. 

```python
#inPDF: skip
from plotting import plot_mission_var

Mprof = Mission(DF70=True)
Mprof.substitutions.update({"t_Mission, Loiter": 6})
Mprof.cost = Mprof["MTOW"]
sol = Mprof.solve("mosek")
fix_vars(Mprof, sol, vars_to_fix)
Mprof.substitutions.update({"P_{pay}": 100})
del Mprof.substitutions["t_Mission, Loiter"]
Mprof.cost = 1/Mprof["t_Mission, Loiter"]
sol = Mprof.solve("mosek")

# plot mission profiles
fig, ax = plot_mission_var(Mprof, sol, "V", [0, 40])
gen_tex_fig(fig, "profile_velocity")

fig, ax = plot_mission_var(Mprof, sol, "h", [0, 20000])
gen_tex_fig(fig, "profile_altitude")

fig, ax = plot_mission_var(Mprof, sol, "\\eta_{prop}", [0, 1])
gen_tex_fig(fig, "profile_etaprop")

fig, ax = plot_mission_var(Mprof, sol, "BSFC", [0, 2])
gen_tex_fig(fig, "profile_BSFC")

fig, ax = plot_mission_var(Mprof, sol, "P_{shaft-max}", [0, 5])
gen_tex_fig(fig, "profile_Pshaftmax")

fig, ax = plot_mission_var(Mprof, sol, "P_{shaft-tot}", [0, 5])
gen_tex_fig(fig, "profile_Pshafttot")

fig, ax = plot_mission_var(Mprof, sol, "RPM", [0, 9000])
gen_tex_fig(fig, "profile_RPM")

fig, ax = plot_mission_var(Mprof, sol, "W_{N+1}", [0, 150], "aircraft weight [lbf]")
gen_tex_fig(fig, "profile_weight")
```
\input{tex/profile_velocity.fig.generated.tex}
\input{tex/profile_etaprop.fig.generated.tex}
\input{tex/profile_BSFC.fig.generated.tex}
\input{tex/profile_Pshaftmax.fig.generated.tex}
\input{tex/profile_Pshafttot.fig.generated.tex}
\input{tex/profile_RPM.fig.generated.tex}
\input{tex/profile_weight.fig.generated.tex}
