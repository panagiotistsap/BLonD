import numpy as np

from ..gpu import block_size, grid_size
from ..gpu.gpu_butils_wrap import d_multscalar, set_zero_int
from ..gpu.gpu_cache import get_gpuarray
from ..utils import bmath as bm

my_gpu = bm.gpuDev()
ker = bm.getMod()

drift = ker.get_function("drift")
kick_kernel = ker.get_function("simple_kick")
rvc = ker.get_function("rf_volt_comp")
dumb_histogram = ker.get_function("histogram")
hybrid_histogram = ker.get_function("hybrid_histogram")
sm_histogram = ker.get_function("sm_histogram")
gm_linear_interp_kick_help = ker.get_function("lik_only_gm_copy")
gm_linear_interp_kick_comp = ker.get_function("lik_only_gm_comp")
gm_linear_interp_kick_drift_comp = ker.get_function("lik_drift_only_gm_comp")
halve_edges = ker.get_function("halve_edges")
beam_phase_v2 = ker.get_function("beam_phase_v2")
beam_phase_sum = ker.get_function("beam_phase_sum")
synch_rad = ker.get_function("synchrotron_radiation")
synch_rad_full = ker.get_function("synchrotron_radiation_full")


def gpu_rf_volt_comp(dev_voltage, dev_omega_rf, dev_phi_rf, dev_bin_centers, dev_rf_voltage, f_rf=0):
    assert dev_voltage.dtype == bm.precision.real_t
    assert dev_omega_rf.dtype == bm.precision.real_t
    assert dev_phi_rf.dtype == bm.precision.real_t
    assert dev_bin_centers.dtype == bm.precision.real_t
    assert dev_rf_voltage.dtype == bm.precision.real_t

    rvc(dev_voltage, dev_omega_rf, dev_phi_rf, dev_bin_centers,
        np.int32(dev_voltage.size), np.int32(
            dev_bin_centers.size), np.int32(f_rf), dev_rf_voltage,
        block=block_size, grid=grid_size, time_kernel=True)


def gpu_kick(dev_dt, dev_dE, dev_voltage, dev_omega_rf, dev_phi_rf, charge, n_rf, acceleration_kick):
    dev_voltage_kick = get_gpuarray(
        (dev_voltage.size, bm.precision.real_t, 0, 'vK'))

    assert dev_dt.dtype == bm.precision.real_t
    assert dev_dE.dtype == bm.precision.real_t
    assert dev_voltage_kick.dtype == bm.precision.real_t
    assert dev_omega_rf.dtype == bm.precision.real_t
    assert dev_phi_rf.dtype == bm.precision.real_t

    d_multscalar(dev_voltage_kick, dev_voltage, charge)

    kick_kernel(dev_dt,
                dev_dE,
                np.int32(n_rf),
                dev_voltage_kick,
                dev_omega_rf,
                dev_phi_rf,
                np.int32(dev_dt.size),
                bm.precision.real_t(acceleration_kick),
                block=block_size, grid=grid_size, time_kernel=True)


def gpu_drift(dev_dt, dev_dE, solver_utf8, t_rev, length_ratio, alpha_order, eta_0,
              eta_1, eta_2, alpha_0, alpha_1, alpha_2, beta, energy):
    solver = solver_utf8.decode('utf-8')
    if solver == "simple":
        solver = np.int32(0)
    elif solver == "legacy":
        solver = np.int32(1)
    else:
        solver = np.int32(2)

    drift(dev_dt,
          dev_dE,
          solver,
          bm.precision.real_t(t_rev), bm.precision.real_t(length_ratio),
          bm.precision.real_t(alpha_order), bm.precision.real_t(eta_0),
          bm.precision.real_t(eta_1), bm.precision.real_t(eta_2),
          bm.precision.real_t(alpha_0), bm.precision.real_t(alpha_1),
          bm.precision.real_t(alpha_2),
          bm.precision.real_t(beta), bm.precision.real_t(energy),
          np.int32(dev_dt.size),
          block=block_size, grid=grid_size, time_kernel=True)


def gpu_linear_interp_kick(dev_dt, dev_dE, dev_voltage,
                           dev_bin_centers, charge,
                           acceleration_kick):
    assert dev_dt.dtype == bm.precision.real_t
    assert dev_dE.dtype == bm.precision.real_t
    assert dev_voltage.dtype == bm.precision.real_t
    assert dev_bin_centers.dtype == bm.precision.real_t

    macros = dev_dt.size
    slices = dev_bin_centers.size

    dev_voltage_kick = get_gpuarray((slices - 1, bm.precision.real_t, 0, 'vK'))
    dev_factor = get_gpuarray((slices - 1, bm.precision.real_t, 0, 'dF'))
    gm_linear_interp_kick_help(dev_dt,
                               dev_dE,
                               dev_voltage,
                               dev_bin_centers,
                               bm.precision.real_t(charge),
                               np.int32(slices),
                               np.int32(macros),
                               bm.precision.real_t(acceleration_kick),
                               dev_voltage_kick,
                               dev_factor,
                               grid=grid_size, block=block_size,
                               time_kernel=True)

    gm_linear_interp_kick_comp(dev_dt,
                               dev_dE,
                               dev_voltage,
                               dev_bin_centers,
                               bm.precision.real_t(charge),
                               np.int32(slices),
                               np.int32(macros),
                               bm.precision.real_t(acceleration_kick),
                               dev_voltage_kick,
                               dev_factor,
                               grid=grid_size, block=block_size,
                               time_kernel=True)


def gpu_linear_interp_kick_drift(dev_voltage,
                                 dev_bin_centers, charge,
                                 acceleration_kick,
                                 T0, length_ratio, eta0, beta, energy,
                                 beam=None):
    assert beam.dev_dt.dtype == bm.precision.real_t
    assert beam.dev_dE.dtype == bm.precision.real_t
    assert dev_voltage.dtype == bm.precision.real_t
    assert dev_bin_centers.dtype == bm.precision.real_t

    macros = beam.dev_dt.size
    slices = dev_bin_centers.size

    dev_voltage_kick = get_gpuarray((slices - 1, bm.precision.real_t, 0, 'vK'))
    dev_factor = get_gpuarray((slices - 1, bm.precision.real_t, 0, 'dF'))

    gm_linear_interp_kick_help(beam.dev_dt,
                               beam.dev_dE,
                               dev_voltage,
                               dev_bin_centers,
                               bm.precision.real_t(charge),
                               np.int32(slices),
                               np.int32(macros),
                               bm.precision.real_t(acceleration_kick),
                               dev_voltage_kick,
                               dev_factor,
                               grid=grid_size, block=block_size,
                               time_kernel=True)
    gm_linear_interp_kick_drift_comp(beam.dev_dt,
                                     beam.dev_dE,
                                     dev_voltage,
                                     dev_bin_centers,
                                     bm.precision.real_t(charge),
                                     np.int32(slices),
                                     np.int32(macros),
                                     bm.precision.real_t(acceleration_kick),
                                     dev_voltage_kick,
                                     dev_factor,
                                     bm.precision.real_t(T0),
                                     bm.precision.real_t(length_ratio),
                                     bm.precision.real_t(eta0),
                                     bm.precision.real_t(beta),
                                     bm.precision.real_t(energy),
                                     grid=grid_size, block=block_size,
                                     time_kernel=True)
    beam.dE_obj.invalidate_cpu()
    beam.dt_obj.invalidate_cpu()


def gpu_dumb_slice(dev_dt, dev_n_macroparticles, cut_left, cut_right):
    """This is only here for benchmarks"""

    n_slices = dev_n_macroparticles.size
    set_zero_int(dev_n_macroparticles)
    dumb_histogram(dev_dt, dev_n_macroparticles, bm.precision.real_t(cut_left),
                   bm.precision.real_t(cut_right), np.uint32(n_slices),
                   np.uint32(dev_dt.size),
                   grid=grid_size, block=block_size, time_kernel=True)
    return dev_n_macroparticles


def gpu_slice(dev_dt, dev_n_macroparticles, cut_left, cut_right):

    assert dev_dt.dtype == bm.precision.real_t

    n_slices = dev_n_macroparticles.size
    set_zero_int(dev_n_macroparticles)
    if 4*n_slices < my_gpu.MAX_SHARED_MEMORY_PER_BLOCK:
        sm_histogram(dev_dt, dev_n_macroparticles, bm.precision.real_t(cut_left),
                     bm.precision.real_t(cut_right), np.uint32(n_slices),
                     np.uint32(dev_dt.size),
                     grid=grid_size, block=block_size, shared=4*n_slices, time_kernel=True)
    else:
        hybrid_histogram(dev_dt, dev_n_macroparticles, bm.precision.real_t(cut_left),
                         bm.precision.real_t(cut_right), np.uint32(n_slices),
                         np.uint32(dev_dt.size), np.int32(
                             my_gpu.MAX_SHARED_MEMORY_PER_BLOCK/4),
                         grid=grid_size, block=block_size, shared=my_gpu.MAX_SHARED_MEMORY_PER_BLOCK, time_kernel=True)
    return dev_n_macroparticles


def gpu_synchrotron_radiation(dE, U0, n_kicks, tau_z):
    assert dE.dtype == bm.precision.real_t
    synch_rad(dE, bm.precision.real_t(U0), np.int32(dE.size), bm.precision.real_t(tau_z),
              np.int32(n_kicks), block=block_size, grid=(my_gpu.MULTIPROCESSOR_COUNT, 1, 1))


def gpu_synchrotron_radiation_full(dE, U0, n_kicks, tau_z, sigma_dE, energy):
    assert dE.dtype == bm.precision.real_t

    synch_rad_full(dE, bm.precision.real_t(U0), np.int32(dE.size),
                   bm.precision.real_t(sigma_dE), bm.precision.real_t(energy),
                   np.int32(n_kicks), np.int32(1), block=block_size, grid=grid_size)


def gpu_beam_phase(bin_centers, profile, alpha, omega_rf, phi_rf, ind, bin_size):
    assert bin_centers.dtype == bm.precision.real_t
    assert profile.dtype == np.int32
    assert omega_rf.dtype == bm.precision.real_t
    assert phi_rf.dtype == bm.precision.real_t

    array1 = get_gpuarray((bin_centers.size, bm.precision.real_t, 0, 'ar1'))
    array2 = get_gpuarray((bin_centers.size, bm.precision.real_t, 0, 'ar2'))

    dev_scoeff = get_gpuarray((1, bm.precision.real_t, 0, 'sc'))
    dev_coeff = get_gpuarray((1, bm.precision.real_t, 0, 'co'))

    beam_phase_v2(bin_centers, profile,
                  bm.precision.real_t(alpha), omega_rf, phi_rf,
                  np.int32(ind), bm.precision.real_t(bin_size),
                  array1, array2, np.int32(bin_centers.size),
                  block=block_size, grid=grid_size)

    beam_phase_sum(array1, array2, dev_scoeff, dev_coeff,
                   np.int32(bin_centers.size), block=(512, 1, 1),
                   grid=(1, 1, 1), time_kernel=True)
    to_ret = dev_scoeff[0].get()
    return to_ret
