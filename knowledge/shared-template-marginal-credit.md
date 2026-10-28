## Problem

The pinned `src/gems57/metric.py` documentation says that a new dot's marginal truth coverage `dT` satisfies `dT <= k`, where `k` is the dot's maximum kernel credit against any one ground-truth pixel. It also describes `dT == k` as the generic non-redundant case. Neither is generally true: `dT` is a **sum over truth pixels**, while `k` is a **maximum for one dot**. One isolated dot can credit several true pixels. This is a mathematical documentation error; this example does **not** show an error in `marginal_accept` or in the competition's default DTI calculation.

Pinned affected file: https://github.com/buffedlizard55-lab/57GEMSDOE/blob/822a0ce5546c7b6749cdd82eb145b6b3e616603d/src/gems57/metric.py#L39-L49

## Synthetic reproduction (no competition data)

```python
import numpy as np
from gems57 import metric
truth = np.zeros((9, 9), bool)
truth[4, 3:6] = True
pred = np.zeros((9, 9))
pred[4, 4] = 1
credit = metric.dti_exact(pred, truth)['tp']
assert np.isclose(credit, 7 / 3)  # center = 1, two neighbors = 2/3 each
assert credit > 1                 # dot's self-credit k is 1
```

## Requested fix in the shared template

Correct the prose and any downstream interpretation that assumes `dT <= k` or calls `dT == k` generally non-redundant. Keep the special-case threshold explicitly conditional on `dT == k`. Add this small multi-truth fixture to the shared template tests. For reference, with old totals `T=TPw`, `F=FPw`, `G=|truth|` and added FP mass `1-k`, the exact improvement criterion is `dT * (alpha*F + beta*G + eps) > alpha*T*(1-k)` for positive denominators. No cached data or leaderboard scores are involved.

This was found while auditing a vendored, pinned copy. We did not patch a private evaluator fork; the actual canonical template for the parallel run remains unspecified.

## Reporting status — 2026-10-28

An attempt to open an upstream issue with this text returned `Resource not accessible by integration (createIssue)`. No upstream issue was created. The authenticated GitHub account has read but not push access to the source repository. This local report does not change or fork the shared template. The separately documented grid-validation issue is [GEMSDOE24 #77](https://github.com/buffedlizard55-lab/GEMSDOE24/issues/77). The canonical shared template for this particular lane is still unresolved.
