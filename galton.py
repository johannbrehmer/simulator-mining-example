import autograd.numpy as np
import autograd as ag

# Default
n_rows = 20
n_nails = 31


# Utils
def sigmoid(x):
    return 1. / (1. + np.exp(-x))


def check_random_state(random_state):
    if isinstance(random_state, int):
        return np.random.RandomState(random_state)
    else:
        return random_state


# Nails
def nail_position(theta, n_rows=n_rows, n_nails=n_nails):
    pos = np.zeros((n_rows, n_nails))
    level = np.broadcast_to(np.arange(n_rows), (n_nails, n_rows)).T

    nail = np.broadcast_to(np.arange(n_nails), (n_rows, n_nails))
    level_rel = 1. * level / (n_rows - 1)
    nail_rel = 2. * nail / (n_nails - 1) - 1.

    return (pos +
            (1. - np.sin(np.pi * level_rel)) * 0.5 +
            np.sin(np.pi * level_rel) * sigmoid(10 * theta * nail_rel))


def threshold(theta, trace):
    begin, z = trace

    pos = begin
    level = 0

    for step in z:
        if step == 0:
            if level % 2 == 0:
                pos = pos
            else:
                pos = pos - 1
        else:
            if level % 2 == 0:
                pos = pos + 1
            else:
                pos = pos
        level += 1

    if level % 2 == 1:  # for odd rows, the first and last nails are constant
        if pos == 0:
            return 0.0
        elif pos == n_nails:
            return 1.0

    level_rel = 1. * level / (n_rows - 1)
    nail_rel = 2. * pos / (n_nails - 1) - 1.
    t = ((1. - np.sin(np.pi * level_rel)) * 0.5 +
         np.sin(np.pi * level_rel) * sigmoid(10 * theta * nail_rel))

    return t


# Run trace and mine gold
def trace(theta, u):
    begin = pos = n_nails // 2
    z = []
    log_p_zx = 0.0

    while len(z) < n_rows:
        t = threshold(theta, (begin, z))
        level = len(z)

        # going left
        if u[level] < t or t == 1.0:
            log_p_zx += np.log(t)

            if level % 2 == 0:  # even rows
                pos = pos
            else:               # odd rows
                pos = pos - 1

            z.append(0)

        # going right
        else:
            log_p_zx += np.log(1. - t)

            if level % 2 == 0:
                pos = pos + 1
            else:
                pos = pos

            z.append(1)

    x = pos

    return log_p_zx, (begin, z, x)

d_trace = ag.grad_and_aux(trace)


# Generator
def galton_rvs(theta, n_runs=100,
               n_rows=n_rows, n_nails=n_nails, random_state=None):
    rng = check_random_state(random_state)
    xs = []
    scores = []
    trajectories = []

    for i in range(n_runs):
        u = rng.rand(n_rows)
        _, (_, _, x) = trace(theta, u)
        d_log_p_zx, (begin, z, x) = d_trace(theta, u)
        xs.append(x)
        scores.append(d_log_p_zx)
        trajectories.append([begin] + z + [x])

    scores = np.array(scores)

    return xs, scores, trajectories[:100]
