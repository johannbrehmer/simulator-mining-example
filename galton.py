import autograd.numpy as np
import autograd as ag

# Default
n_rows = 20
n_nails = 31


# Utils
def sigmoid(x):
    return 1. / (1. + np.exp(-x))


def check_random_state(random_state):
    if random_state is None or isinstance(random_state, int):
        return np.random.RandomState(random_state)
    else:
        return random_state


# Nails
def nail_positions(theta, n_rows=n_rows, n_nails=n_nails):
    pos = np.zeros((n_rows, n_nails))
    level = np.broadcast_to(np.arange(n_rows), (n_nails, n_rows)).T

    nail = np.broadcast_to(np.arange(n_nails), (n_rows, n_nails))
    level_rel = 1. * level / (n_rows - 1)
    nail_rel = 2. * nail / (n_nails - 1) - 1.

    return (
        pos
        + (1. - np.sin(np.pi * level_rel)) * 0.5
        + np.sin(np.pi * level_rel) * sigmoid(10 * theta * nail_rel)
    )


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
    t = (1. - np.sin(np.pi * level_rel)) * 0.5 + np.sin(np.pi * level_rel) * sigmoid(
        10 * theta * nail_rel
    )

    return t


# Run and mine gold
def trace(theta, u, theta_ref=None):
    if theta_ref is None:
        theta_ref = theta

    begin = pos = n_nails // 2
    z = []
    log_p_xz = 0.0

    while len(z) < n_rows:
        t_ref = threshold(theta_ref, (begin, z))
        t = threshold(theta, (begin, z))
        level = len(z)

        # going left
        if u[level] < t_ref or t_ref == 1.0:
            log_p_xz += np.log(t)

            if level % 2 == 0:  # even rows
                pos = pos
            else:  # odd rows
                pos = pos - 1

            z.append(0)

        # going right
        else:
            log_p_xz += np.log(1. - t)

            if level % 2 == 0:
                pos = pos + 1
            else:
                pos = pos

            z.append(1)

    x = pos

    return log_p_xz, (begin, z, x)


d_trace = ag.grad_and_aux(trace)


# Generator
def galton_rvs(theta, n_runs=100, n_rows=n_rows, n_nails=n_nails, random_state=None):
    rng = check_random_state(random_state)
    all_x = []
    all_log_p_xz = []
    all_t_xz = []
    trajectories = []

    for i in range(n_runs):
        u = rng.rand(n_rows)
        log_p_xz, (begin, z, x) = trace(theta, u)
        t_xz, _ = d_trace(theta, u)
        all_x.append(x)
        all_log_p_xz.append(log_p_xz)
        all_t_xz.append(t_xz)
        trajectories.append([begin] + z + [x])

    all_log_p_xz = np.array(all_log_p_xz)
    all_t_xz = np.array(all_t_xz)

    return all_x, all_log_p_xz, all_t_xz, trajectories


def galton_rvs_ratio(
    theta0, theta1, n_runs=100, n_rows=n_rows, n_nails=n_nails, random_state=None
):
    rng = check_random_state(random_state)
    all_x = []
    all_log_p_xz_0 = []
    all_t_xz_0 = []
    all_log_p_xz_1 = []
    all_t_xz_1 = []
    trajectories = []

    for i in range(n_runs):
        u = rng.rand(n_rows)
        log_p_xz_0, (begin, z, x) = trace(theta0, u)
        t_xz_0, _ = d_trace(theta0, u)
        all_x.append(x)
        all_log_p_xz_0.append(log_p_xz_0)
        all_t_xz_0.append(t_xz_0)
        trajectories.append([begin] + z + [x])

        log_p_xz_1, _ = trace(theta1, u, theta_ref=theta0)
        t_xz_1, _ = d_trace(theta1, u, theta_ref=theta0)
        all_log_p_xz_1.append(log_p_xz_1)
        all_t_xz_1.append(t_xz_1)

    all_log_p_xz_0 = np.array(all_log_p_xz_0)
    all_t_xz_0 = np.array(all_t_xz_0)
    all_log_p_xz_1 = np.array(all_log_p_xz_1)
    all_t_xz_1 = np.array(all_t_xz_1)

    return all_x, all_log_p_xz_0, all_log_p_xz_1, all_t_xz_0, all_t_xz_1, trajectories
