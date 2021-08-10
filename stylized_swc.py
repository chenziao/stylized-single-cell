import numpy as np
import pandas as pd
from copy import deepcopy
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt

def gen_stylized_swc(geometry,dL=5.0):
    # geometry: pandas dataframe of geometry parameters
    # dL: um. segment maximun length (cannot be too big, otherwise will cause error in bmtk)
    secs = []
    end_id = []
    idx_list = [0]
    row0 = [0,0.,0.,0.,0.,1]
    for j,sec in geometry.iterrows():
        row = row0.copy()
        row[0] = sec['type']
        if sec['axial']:
            row[1:4] = [0.,sec['L']*np.sin(sec['ang']),0.]
        else:
            row[1:4] = [sec['L']*np.cos(sec['ang']),sec['L']*np.sin(sec['ang']),0.]
        row[4] = sec['R']
        if sec['type']==1:
            row[5] = -1
        nseg = max(np.ceil(sec['L']/dL).astype(int),1)
        rows = [row.copy() for _ in range(nseg)]
        ids = np.arange(nseg)+idx_list[-1]+1
        for i, r in enumerate(rows):
            r[1:4] = (i+1)/nseg*np.array(r[1:4])
        if sec['pid']>0:
            rows[0][5] = end_id[sec['pid']]
            y_shift = secs[rows[0][5]-1][2]
            for r in rows:
                r[2] = r[2]+y_shift
        for (r,i) in zip(rows[1:],ids[:-1]):
            r[5] = i
        idx_list.extend(ids)
        secs.extend(deepcopy(rows))
        if sec['axial']:
            end_id.append(ids[-1])
        else:
            end_id.append(1)
            ids += nseg
            for r in rows:
                r[1] = -r[1]
            for (r,i) in zip(rows[1:],ids[:-1]):
                r[5] = i
            idx_list.extend(ids)
            secs.extend(rows)
    
    stylized = pd.DataFrame(data=secs,columns=['type','x','y','z','r','pid'],index=idx_list[1:])
    stylized.index.name = 'id'
    return stylized

# define plot morphology function
def plot_morphology_swc(swc_full,child_idx=None,root_id=None,ax=None,figsize=(8,6),clr=['g','r','b','c']):
    seg_type = ['soma','axon','dend','apic']
    coor3d = list('xyz')
    rm = swc_full.loc[swc_full['type']!=1,'r'].mean()
    if child_idx is None:
        swc = swc_full
    else:
        swc = swc_full.loc[child_idx]
    ilab = []
    for i in range(4):
        try:
            ilab.append(list(swc['type']==i+1).index(True))
        except:
            ilab.append(-1)
    if root_id is None:
        root_id = swc_full.index[swc_full['pid']<0][0]
    if ax is None:
        fig = plt.figure(figsize=figsize)
        ax = plt.axes(projection='3d')
    else:
        fig = ax.figure
    for i, idx in enumerate(swc.index):
        label = str(ilab.index(i)+1)+': '+seg_type[ilab.index(i)] if i in ilab else None
        typeid = swc.loc[idx,'type']
        if typeid==1:
            ax.scatter(*swc.loc[idx,coor3d],c=clr[0],s=swc.loc[idx,'r']/rm,label=label)
        else:
            pid = swc.loc[idx,'pid']
            if pid is not root_id:
                line = np.vstack((swc.loc[idx,coor3d],swc_full.loc[pid,coor3d]))
                ax.plot3D(line[:,0],line[:,1],line[:,2],color=clr[typeid-1],
                          linewidth=.5*swc.loc[idx,'r']/rm,label=label)
    ax.legend()
    plt.show()
    return fig,ax
