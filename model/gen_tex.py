from gpkit.small_scripts import unitstr
import gpkit

latex_opers = {"<=": " \\leq ", ">=": " \\geq ", "=": " = "}

def cleaned_latex(model):
    latex = model.latex(excluded=["units"])
    varnames = frozenset(vk.name for vk in model.varkeys)
    for name in varnames:
        vks_orig = [var.key for var in model.variables_byname(name)
                    if var.key.latex(excluded=["units"]) in latex]
        for var in model.variables_byname(name):
            vk = var.key
            if vk.veckey:
                if vk.veckey.latex(excluded=["units"]) in latex:
                    if vk.veckey not in vks_orig:
                        vks_orig.append(vk.veckey)
        vkds = [vk.descr.copy() for vk in vks_orig]
        if not vkds:
            continue
        elif len(vkds) == 1:
            vkd = vkds[0]
            vkd.pop("models", None)
        if all("models" in vkd for vkd in vkds):
            successes = 0
            for i, modelname in enumerate(list(vkds[0]["models"])):
                try:
                    i = i - successes
                    if all(vkd["models"][i] == modelname
                           for vkd in vkds):
                        successes += 1
                        for vkd in vkds:
                            vkd["models"] = list(vkd["models"])
                            vkd["models"].pop(i)
                except IndexError:
                    break

            successes = 0
            for i, modelname in enumerate(reversed(list(vkds[0]["models"]))):
                try:
                    i = -1 - i + successes
                    if all(vkd["models"][i] == modelname
                           for vkd in vkds):
                        successes += 1
                        for vkd in vkds:
                            vkd["models"] = list(vkd["models"])
                            vkd["models"].pop(i)
                except IndexError:
                    break
            for vkd in vkds:
                if (all(vkd_b["models"] in [vkd["models"], []]
                          for vkd_b in vkds if vkd_b != vkd)
                      and not any(vkd_b.get("idx", None) == vkd.get("idx", None) for vkd_b in vkds if vkd_b != vkd)):
                    vkd["models"] = []
            for vkd in vkds:
                if not vkd["models"]:
                    del vkd["models"]
                    del vkd["modelnums"]
        vks = [gpkit.VarKey(**vkd) for vkd in vkds]
        assert len(vks) == len(vks_orig)
        for vk, vk_orig in zip(vks, vks_orig):
            latex = latex.replace(vk_orig.latex(excluded=["units"]),
                                  vk.latex(excluded=["units"]))
    return latex



def gen_model_tex(model, modelname, texname=None):
    if texname:
        filename = texname
    else:
        filename = modelname
    with open('tex/%s.vars.generated.tex' % filename, 'w') as f:
        f.write("\\begin{longtable}{llll}\n \\toprule\n")
        f.write("\\toprule\n")
        f.write("Variables & Value & Units & Description \\\\ \n")
        f.write("\\midrule\n")
        #f.write("\\multicolumn{3}{l}\n")
        varnames = ["firstname"]
        for var in model.varkeys:
            name = var.name
            if name in varnames:
                pass
            else:
                if var.models[-1] == modelname:
                    varnames.append(name)
                    unitstring = var.unitstr()[1:]
                    unitstring = "$[%s]$" % unitstring if unitstring else ""
                    val = "%0.3f" % var.value if var.value else ""
                    f.write("$%s$ & %s & %s & %s \\\\\n" %
                            (var.name, val, unitstring, var.label))
                else:
                    pass
        f.write("\\bottomrule\n")
        f.write("\\end{longtable}\n")

    with open('tex/%s.cnstrs.generated.tex' % filename, 'w') as f:
        lines = []
        for cs in model:
            if not hasattr(cs, "__len__"):
                cs = [cs]
            for eq in cs:
                if isinstance(eq, gpkit.nomials.nomial_math.ScalarSingleEquationConstraint):
                    lines.append(eq.latex(excluded=["models", "units"]))
                elif isinstance(eq, gpkit.constraints.array.ArrayConstraint):
                    if hasattr(eq, "__len__"):
                        eq = eq[0]
                    if hasattr(eq.left, "__len__"):
                        left = eq.left[0].latex(excluded=["models", "units",
                                                          "idx"])
                    else:
                        left = eq.left.latex(excluded=["models", "units",
                                                       "idx"])
                    if hasattr(eq.right, "__len__"):
                        right = eq.right[0].latex(excluded=["models", "units",
                                                            "idx"])
                    else:
                        right = eq.right.latex(excluded=["models", "units",
                                                         "idx"])
                    oper = latex_opers[eq.oper]
                    lines.append(left+oper+right)

        for l in lines:
            f.write("$$ %s $$" % l)

def find_models(csets, used_cset=[], models=[], modelnames=[]):
    runagain = 0
    for c in csets:
        if c not in used_cset:
            used_cset.append(c)
            for m in c:
                if type(m) == gpkit.ConstraintSet:
                    csets.append(m)
                    runagain = 1
                else:
                    if isinstance(m, gpkit.Model):
                        if m.__class__.__name__ not in modelnames:
                            models.append(m)
                            modelnames.append(m.__class__.__name__)

    if runagain == 0:
        return models, modelnames
    elif runagain != 0:
        return find_models(csets, used_cset, models, modelnames)

def find_submodels(models, modelnames, used_models=[]):
    runagain = 0
    for m in models:
        if m not in used_models:
            used_models.append(m)
            for subm in m:
                if type(subm) == gpkit.ConstraintSet:
                    cmodels, cmns = find_models([subm])
                    for cm in cmodels:
                        if cm.__class__.__name__ not in modelnames:
                            models.append(cm)
                            modelnames.append(cm.__class__.__name__)
                            runagain = 1
                else:
                    if isinstance(subm, gpkit.Model):
                        if subm.__class__.__name__ not in modelnames:
                            models.append(subm)
                            modelnames.append(subm.__class__.__name__)
                            runagain = 1

    if runagain > 0:
        return find_submodels(models, modelnames, used_models)
    else:
        return models, modelnames

def gen_tex_fig(fig, filename, caption=None):
    fig.savefig("figs/%s.pdf" % filename)
    with open("tex/%s.fig.generated.tex" % filename, "w") as f:
        f.write("\\begin{figure}[H]\n")
        f.write("\\label{f:%s}\n" % filename)
        f.write("\\begin{center}\n")
        f.write("\\includegraphics[scale=0.5]{figs/%s}\n" % filename)
        if caption:
            f.write("\\caption{%s}\n" % caption)
        f.write("\\end{center}\n")
        f.write("\\end{figure}\n")

def gen_fixvars_tex(model, solution, fixvars, filename=None):
    if filename:
        texname = "%s.table.generated.tex" % filename
    else:
        texname = "tex/fixvars.table.generated.tex"
    with open(texname, 'w') as f:
        f.write("\\begin{longtable}{lllll}\n \\toprule\n")
        f.write("\\toprule\n")
        f.write("Variables & Value & Units & Description \\\\ \n")
        f.write("\\midrule\n")
        for varname in fixvars:
            name = model[varname].descr["name"]
            val = "%0.3f" % solution(varname).magnitude
            unitstring = unitstr(model[varname].units)
            label = model[varname].descr["label"]
            if varname in solution["sensitivities"]["constants"]:
                sens = "%0.3f" % solution["sensitivities"]["constants"][varname]
            else:
                sens = ""
            f.write("$%s$ & %s & %s & %s & %s \\\\\n" %
                    (name, val, unitstring, sens, label))
        f.write("\\bottomrule\n")
        f.write("\\end{longtable}\n")
