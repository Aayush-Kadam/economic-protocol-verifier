from __future__ import annotations
from fractions import Fraction
from itertools import product

def auction_severity(m):
    max_gain=(Fraction(0),None); max_ir=(Fraction(0),None); max_deficit=(Fraction(0),None); max_loss=(Fraction(0),None)
    n=len(m.agents)
    for types in m.domain.type_profiles():
        out=m.outcome(types)
        for i,theta in enumerate(types):
            u=m.utility(i,theta,out); short=m.outside_options[i]-u
            if short>max_ir[0]: max_ir=(short,{"agent":i,"types":types})
            others=tuple(j for j in range(n) if j!=i)
            for vals in product(*(m.domain.report_spaces[j] for j in others)):
                truthful=list(vals); truthful.insert(i,theta); tu=m.utility(i,theta,m.outcome(tuple(truthful)))
                for d in m.domain.report_spaces[i]:
                    report=list(truthful); report[i]=d; gain=m.utility(i,theta,m.outcome(tuple(report)))-tu
                    witness={"agent":i,"true_type":theta,"truthful_reports":tuple(truthful),"deviation_reports":tuple(report)}
                    if gain>max_gain[0] or gain==max_gain[0] and max_gain[1] is not None and str(witness)<str(max_gain[1]): max_gain=(gain,witness)
        loss=max(m.welfare(types,a) for a in m.feasible_allocations)-m.welfare(types,out.allocation)
        if loss>max_loss[0]: max_loss=(loss,{"types":types})
    for reports in m.domain.report_profiles():
        deficit=-sum(m.outcome(reports).transfers)
        if deficit>max_deficit[0]: max_deficit=(deficit,{"reports":reports})
    return {"property_id":"epv.auction.severity_metrics.v1","max_manipulation_gain":max_gain,"max_ir_shortfall":max_ir,"max_deficit":max_deficit,"max_welfare_loss":max_loss}
