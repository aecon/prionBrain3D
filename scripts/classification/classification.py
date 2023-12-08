import os
import pickle
import argparse
import numpy as np
#from sklearn import preprocessing
#from sklearn.metrics import confusion_matrix
#from sklearn.metrics import accuracy_score
#from sklearn.ensemble import RandomForestClassifier
#
#import scipy.ndimage
#import skimage.restoration

import img3


SCALER = "classifier/scaler.pkl"
CLASSIFIER = "classifier/classifier.pkl"


def nrrd_details(fnrrd):
    nrrd        = img3.nrrd_read(fnrrd)
    dtype       = nrrd["type"]
    path        = nrrd["path"]
    shape       = nrrd["sizes"]
    offset      = nrrd.get("byte skip", 0)
    dx, dy, dz  = nrrd.get("spacings")
    return dtype, path, shape, offset, dx, dy, dz


def lst_to_features(odir, lst_pickle, denoised_nrrd):

    #odir = "%s/features" % dataset.output_directory
    #lst_pickle = dataset.lst_pickle
    #denoised_nrrd = dataset.denoised_nrrd

    if not os.path.exists(odir):
        os.makedirs(odir)

    print("read denoised raw/nrrd")
    dtype, path, shape, offset, dx, dy, dz = nrrd_details(denoised_nrrd)
    denoised = np.memmap(path, dtype, 'r', offset=offset, shape=shape, order='F')

    print("read lst pickle")
    with open(lst_pickle, 'rb') as fl:
        lst = pickle.load(fl)

    print("compute counts")
    Nc = len(lst)
    print(Nc)
    counts = np.zeros(Nc)
    for idx,l in enumerate(lst):
        counts[idx] = l.shape[0]

    print("sort by volume")
    sort_idx = np.argsort(counts)

    Nc = len(lst)
    labels    = np.zeros(Nc, dtype=np.dtype(np.uint32))
    counts    = np.zeros(Nc, dtype=np.dtype(np.uint32))
    int_max   = np.zeros(Nc, dtype=np.dtype(np.float32))
    int_avg   = np.zeros(Nc, dtype=np.dtype(np.float32))
    int_std   = np.zeros(Nc, dtype=np.dtype(np.float32))
    obj_lx2   = np.zeros(Nc, dtype=np.dtype(np.float32))
    obj_ly2   = np.zeros(Nc, dtype=np.dtype(np.float32))
    obj_lz2   = np.zeros(Nc, dtype=np.dtype(np.float32))
    obj_Rg    = np.zeros(Nc, dtype=np.dtype(np.float32))
    obj_asph  = np.zeros(Nc, dtype=np.dtype(np.float32))
    obj_acyl  = np.zeros(Nc, dtype=np.dtype(np.float32))
    obj_kappa = np.zeros(Nc, dtype=np.dtype(np.float32))
    obj_lmax  = np.zeros(Nc, dtype=np.dtype(np.float32))
    obj_lmin  = np.zeros(Nc, dtype=np.dtype(np.float32))
    obj_Vrs   = np.zeros(Nc, dtype=np.dtype(np.float32))
    obj_Vre   = np.zeros(Nc, dtype=np.dtype(np.float32))

    print("loop over objects")
    for idx,i0 in enumerate(sort_idx):
        l = lst[i0]
        assert(l.shape[0] > 0)

        labels[idx] = idx

        vol = l.shape[0]
        counts[idx] = vol

        # intensities
        Intensities = denoised[l[:,0], l[:,1], l[:,2]]
        int_max[idx] = np.max(Intensities)
        int_avg[idx] = np.mean(Intensities)
        int_std[idx] = np.std(Intensities) / int_avg[idx]

        # gyration tensor
        l = np.asarray(l, dtype=np.float64)
        l -= np.mean(l, axis = 0)
        GT = (np.dot(l.T, l)) / vol
        lambdas, ev = np.linalg.eig(GT)
        lx2, ly2, lz2 = np.sort(lambdas)  # CONVENTION: lx <= ly <= lz
        assert(lx2<=ly2 and ly2<=lz2)
        obj_lx2[idx] = lx2
        obj_ly2[idx] = ly2
        obj_lz2[idx] = lz2

        asph = lz2 - 0.5*(lx2+ly2)
        Rg2 = lx2 + ly2 + lz2
        acyl = ly2 - lx2
        kappa = (asph*asph + (3./4.)*acyl*acyl) / (Rg2*Rg2)  # [0, 1]
        assert(kappa>=0 and kappa<=1)
        obj_Rg[idx] = np.sqrt(Rg2)
        obj_asph[idx] = asph
        obj_acyl[idx] = acyl
        obj_kappa[idx] = kappa

        # eigendecomposition of covariance matrix
        C = np.cov(l.T)
        eVa, eVe = np.linalg.eig(C)
        Q = np.dot(l, eVe)

        # extensions
        box_lo = np.amin(Q, axis=0)
        box_hi = np.amax(Q, axis=0)
        extents = box_hi - box_lo
        extents = np.sort(extents)[::-1]
        Lmax = extents[0]
        Lmin = extents[1]
        obj_lmax[idx] = Lmax
        obj_lmin[idx] = Lmin

        # flatness
        Rg = np.sqrt( np.sum(l*l) / vol )
        Vsphere = 4./3.*np.pi*pow(Rg,3) * pow((5./3.), (3./2.))
        Vr = vol / Vsphere
        obj_Vrs[idx] = Vr

        # fit ellipsoid
        lx = np.sqrt(lx2)
        ly = np.sqrt(ly2)
        lz = np.sqrt(lz2)
        Vellipse = 4./3. * np.pi * lx * ly * lz * pow(3, (3./2.)) * pow((5./3.), (3./2.)) 
        Vre = vol / Vellipse
        obj_Vre[idx] = Vre

    # save to file
    header = "label vol Imax Iavg Istd lx2 ly2 lz2 Rg asph acyl kappa Lmax Lmin Vrs Vre"
    features = np.c_[labels, counts, int_max, int_avg, int_std, obj_lx2, obj_ly2, obj_lz2, obj_Rg, obj_asph, obj_acyl, obj_kappa, obj_lmax, obj_lmin, obj_Vrs, obj_Vre]
    np.savetxt("%s/candidates_features.dat" % odir, features, header=header, fmt='%.16e')



def classify(odir, lst_pickle_file, denoised_nrrd):

    lst_to_features(odir, lst_pickle_file, denoised_nrrd)

    features_file = "%s/candidates_features.dat" % odir

    # data
    # 'idx(sorted)', 'vol', 'Imax', 'Iavg', 'Istd', 'lx2', 'ly2', 'lz2', 'Rg', 'asph', 'acyl', 'kappa', 'Lmax', 'Lmin', 'Vrs', 'Vre'
    #      0           1       2       3       4      5      6      7      8      9      10      11      12       13      14     15
    X0 = np.loadtxt(features_file, skiprows=1)
    idxE = np.prod(np.isfinite(X0), axis=1) # remove rows with nan/inf
    X   = X0[:, 2::]
    vol = X0[:, 1]
    X[idxE==0, -1] = 0
    vol[idxE==0] = 0

    # load scaler
    with open(SCALER, 'rb') as fl:
        scaler = pickle.load(fl)
    print("Loaded scaler")

    # regularization
    X_scaled = scaler.transform(X)

    # load classifier
    with open(CLASSIFIER, 'rb') as fl:
        classifier = pickle.load(fl)
    print("Loaded classifier")

    # prediction
    y_pred = classifier.predict(X_scaled)
    print("Generated predictions")


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # WRITE BINARY ARRAY WITH PREDICTED CELLS
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # denoised shape and pixels spacings (here: 1,1,1) ..
    dtype, path, shape, offset, dx, dy, dz = nrrd_details(denoised_nrrd)
    print("Read denoised.nrrd")

    # new cells array
    cells8 = img3.mmap_create("%s/cells.raw" % os.path.dirname(denoised_nrrd), np.dtype("uint8"), shape)
    img3.nrrd_write("%s/cells.nrrd" % os.path.dirname(denoised_nrrd), "%s/cells.raw" % os.path.dirname(denoised_nrrd), cells8.dtype, cells8.shape, (dx,dy,dz))
    img3.memset(cells8, 0)
    print("img3.memset(cells8, 0)")

    # list of objects
    with open(lst_pickle_file, 'rb') as fl:
        lst = pickle.load(fl)
    Nc = len(lst)
    counts = np.zeros(Nc)
    for idx,l in enumerate(lst):
        counts[idx] = l.shape[0]
    sort_idx = np.argsort(counts)
    print("Sorted counts")
    print(len(sort_idx), len(lst), len(y_pred))


    # loop over candidate cells
    for idx,i0 in enumerate(sort_idx):
        if y_pred[idx]==1 and idxE[idx]==1:
            l = lst[i0]
            assert(l.shape[0] > 0)
            cells8[l[:,0], l[:,1], l[:,2]] = 1
   


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-l', type=str, required=True, help="lst pickle file")
    parser.add_argument('-d', type=str, required=True, help="denoised nrrd (normalized)")
    args = parser.parse_args()

    odir = "%s/out_classification" % os.path.dirname(args.l)
    if not os.path.exists(odir):
        os.makedirs(odir)

    classify(odir, args.l, args.d)


