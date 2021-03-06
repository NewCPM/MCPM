import numpy as np
from scipy.optimize import minimize
from os import path
import matplotlib.pyplot as plt
import sys

from MCPM import utils
from MCPM.cpmfitsource import CpmFitSource

    
def fun_3(inputs, cpm_source, t_E):
    """3-parameter function for optimisation; t_E - fixed"""
    t_0 = inputs[0]
    u_0 = inputs[1]
    t_E = t_E
    f_s = inputs[2]
    if u_0 < 0. or t_E < 0. or f_s < 0.:
        return 1.e6
        
    model = cpm_source.pspl_model(t_0, u_0, t_E, f_s)
    cpm_source.run_cpm(model)        

    #print(t_0, u_0, t_E, f_s, cpm_source.residuals_rms)
    return cpm_source.residuals_rms

def fun_4(inputs, cpm_source):
    """4-parameter function for optimisation"""
    t_0 = inputs[0]
    u_0 = inputs[1]
    t_E = inputs[2]
    f_s = inputs[3]    
    if u_0 < 0. or t_E < 0. or f_s < 0.:
        return 1.e6

    model = cpm_source.pspl_model(t_0, u_0, t_E, f_s)
    cpm_source.run_cpm(model)        
    
    #print(t_0, u_0, t_E, f_s, cpm_source.residuals_rms)
    return cpm_source.residuals_rms
    

if __name__ == "__main__":
    # We want to extract the light curve of ob160980
    channel = 52
    campaign = 92
    ra = 271.354292
    dec = -28.005583

    half_size = 2
    n_select = 10
    l2 = 10**8.5
    start = np.array([7556., 0.14, 21., 300.])
    start_3 = np.array([7556., .1, 150.])
    t_E = 21.
    tol = 0.001
    #method = 'Nelder-Mead' # only these 2 make sense
    method = 'Powell'
    n_remove = 10
    
    cpm_source = CpmFitSource(ra=ra, dec=dec, campaign=campaign, 
            channel=channel)
    
    cpm_source.get_predictor_matrix() #n_pixel=100)
    cpm_source.set_l2_l2_per_pixel(l2=l2)
    cpm_source.set_pixels_square(half_size)
    cpm_source.select_highest_prf_sum_pixels(n_select)

    # Optimize model parameters:
    args = (cpm_source, t_E)
    out = minimize(fun_3, start_3, args=args, tol=tol, method=method)
    print(out)
    
    # plot the best model
    model = cpm_source.pspl_model(out.x[0], out.x[1], t_E, out.x[2])
    cpm_source.run_cpm(model)
    print("RMS: {:.4f}  {:}".format(cpm_source.residuals_rms, np.sum(cpm_source.residuals_mask)))
    
    cpm_source.run_cpm_and_plot_model(model, plot_residuals=True, f_s = out.x[2])
    #plt.show()
    plt.close()
    
    # you may want to plot residuals as a function of position:
    if False:
        plt.scatter(cpm_source.x_positions[mask], cpm_source.y_positions[mask], c=np.abs(cpm_source.residuals[mask]))
        plt.show()
        plt.close()
    
    # Remove most outlying points:
    if True:
        mask = cpm_source.residuals_mask
        limit = np.sort(np.abs(cpm_source.residuals[mask]))[-n_remove]
        cpm_source.mask_bad_epochs_residuals(limit)
        model = cpm_source.pspl_model(out.x[0], out.x[1], t_E, out.x[2])
        cpm_source.run_cpm(model)
        print("RMS: {:.4f}  {:}".format(cpm_source.residuals_rms, np.sum(cpm_source.residuals_mask)))

    # Optimize model parameters once more:
    if True:
        out = minimize(fun_3, out.x, args=args, tol=tol, method=method)
        print(out)
        
        model = cpm_source.pspl_model(out.x[0], out.x[1], t_E, out.x[2])
        cpm_source.run_cpm(model)
        print("RMS: {:.4f}  {:}".format(cpm_source.residuals_rms, np.sum(cpm_source.residuals_mask)))
        
        # plot it:
        if True:
            cpm_source.run_cpm_and_plot_model(model, plot_residuals=True, f_s = out.x[2])
            #plt.savefig('ob160980.png')
            plt.show()
            plt.close()
            
            cpm_source.plot_pixel_residuals()
            #plt.savefig('ob160980_pixel_res.png')
            plt.show()
            plt.close()

    # Optimize model parameters with 4 fitted parameters:
    if False:
        args = (cpm_source)
        out = minimize(fun_4, start, args=args, tol=tol, method=method)
        print(out)
    #print(out.nfev)
    #print("{:.5f} {:.4f} {:.4f}  ==> {:.4f}".format(out.x[0], out.x[1], out.x[2], out.fun))
    
    #model = transform_model(out.x[0], out.x[1], out.x[2], model_dt, model_flux, cpm_source.pixel_time)
        model = cpm_source.pspl_model(out.x[0], out.x[1], out.x[2], out.x[3])
        cpm_source.run_cpm(model)
        mask = cpm_source.residuals_mask
        plt.plot(cpm_source.pixel_time[mask], cpm_source.residuals[mask]+model[mask], '.')
        plt.show()
