import math
import numpy as np
from scipy import stats
from _dataprep import load, approach, reop_set, has_necrosis

D = load()
R = reop_set()
malrot, first = D["malrot"], D["first"]
R = {p for p in R if p in set(malrot)}
AGED = D["age_d"]

lapv = np.array([1.0 if approach(first[p]) == "腹腔镜完成" else 0.0 for p in malrot])
necv = np.array([1.0 if has_necrosis(first[p]) else 0.0 for p in malrot])
aged = np.array([AGED[p] if AGED.get(p) is not None else np.nan for p in malrot])
neov = (aged < 28).astype(float)
b28 = (aged >= 28).astype(float)
b365 = (aged >= 365.25).astype(float)
yall = np.array([1.0 if p in R else 0.0 for p in malrot])


def firth_fit(X, y, fixed=None, max_iter=500, tol=1e-10):
    n, p = X.shape; beta = np.zeros(p)
    free = [j for j in range(p) if fixed is None or j != fixed[0]]
    if fixed is not None: beta[fixed[0]] = fixed[1]
    for _ in range(max_iter):
        eta = X @ beta; pr = 1 / (1 + np.exp(-eta)); W = pr * (1 - pr)
        XtWX = X.T @ (X * W[:, None]); Ainv = np.linalg.pinv(XtWX)
        h = np.sum((X @ Ainv) * X, axis=1) * W
        U = X.T @ (y - pr + h * (0.5 - pr))
        step = np.linalg.pinv(XtWX[np.ix_(free, free)]) @ U[free]
        beta[free] += step
        if np.max(np.abs(step)) < tol: break
    return beta


def firth_pll(X, y, beta):
    eta = X @ beta; pr = np.clip(1 / (1 + np.exp(-eta)), 1e-12, 1 - 1e-12)
    ll = np.sum(y * np.log(pr) + (1 - y) * np.log(1 - pr))
    W = pr * (1 - pr); _, ld = np.linalg.slogdet(X.T @ (X * W[:, None]))
    return ll + 0.5 * ld


def firth(y, covs, label):
    X = np.column_stack([np.ones(len(y)), lapv] + covs)
    b = firth_fit(X, y)
    eta = X @ b; pr = 1 / (1 + np.exp(-eta)); W = pr * (1 - pr)
    se = np.sqrt(np.diag(np.linalg.pinv(X.T @ (X * W[:, None]))))
    b0 = firth_fit(X, y, fixed=(1, 0.0))
    p = stats.chi2.sf(max(2 * (firth_pll(X, y, b) - firth_pll(X, y, b0)), 0), 1)
    return (label, math.exp(b[1]), math.exp(b[1] - 1.96 * se[1]),
            math.exp(b[1] + 1.96 * se[1]), p)


for covs, lab in [([], "Firth, unadjusted"),
                  ([neov, necv], "Firth + neonate (<28 days) + index necrosis"),
                  ([b28, b365, necv], "Firth + age band + index necrosis")]:
    lab_, orv, lo, hi, p = firth(yall, covs, lab)
    print("%-45s OR = %.4f  95%% CI = %.4f - %.4f  p = %.6f" % (lab_, orv, lo, hi, p))
