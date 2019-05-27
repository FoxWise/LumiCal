'''
This file includes information for the LumiCal TestBeam2016:
###APV maps###
APV's channel -> pad id:

     0           1         2         3
 _________________________________________
|   63     |    127   |   191   |   255   |
|-----------------------------------------|
 |   62    |    126   |   190   |  254   |
 |---------------------------------------|
  |   61    |   125   |   189  |  253   |
  |-------------------------------------|

         .........................
         .........................

         |  0  |  64 | 128 | 192 |
         |_____|_____|_____|_____|
#######

###CalibFiles###
Energy calibration files for APVs
######

###Hit###
Hit object with certain position and energy
######

Number of APVs: 16
Number of channels of one APV: 128
Number of layers in experiment: 6(7) 0,1 - trackers, >2 - calorimeter
Number of sectors in the one layer: 4
Number of pads in one sector: 64
'''
from ROOT import TGraphErrors, TMath
import numpy as np
import random
from itertools import islice


class ApvMaps:
    ''' Maps of apv channels to pad number. Are taken from Sasha  analysis code'''
    tb15_master = [190 - i if i < 63 else i + 129 for i in range(127)] + [-1]

    tb15_slave = [-1, 62, 63, 60, 61, 58, 59, 56, 57, 54, 55, 52, 53, 50, 51,
                  48, 49, 46, 47, 44, 45, 42, 43, 40, 41, 38, 39, 36, 37, 34,
                  35, 32, 33, 30, 31, 28, 29, 26, 27, 24, 25, 22, 23, 20, 21,
                  18, 19, 16, 17, 14, 15, 12, 13, 10, 11, 8, 9, 6, 7, 4, 5,
                  2, 3, 0, 1, 65, 64, 67, 66, 69, 68, 71, 70, 73, 72, 75, 74,
                  77, 76, 79, 78, 81, 80, 83, 82, 85, 84, 87, 86, 89, 88, 91,
                  90, 93, 92, 95, 94, 97, 96, 99, 98, 101, 100, 103, 102, 105,
                  104, 107, 106, 109, 108, 111, 110, 113, 112, 115, 114, 117,
                  116, 119, 118, 121, 120, 123, 122, 125, 124, 127]

    tb15_slave = [-1, 62, 63, 60, 61, 58, 59, 56, 57, 54, 55, 52, 53, 50, 51,
                  48, 49, 46, 47, 44, 45, 42, 43, 40, 41, 38, 39, 36, 37, 34,
                  35, 32, 33, 30, 31, 28, 29, 26, 27, 24, 25, 22, 23, 20, 21,
                  18, 19, 16, 17, 14, 15, 12, 13, 10, 11, 8, 9, 6, 7, 4, 5, 2,
                  3, 0, 1, 65, 64, 67, 66, 69, 68, 71, 70, 73, 72, 75, 74, 77,
                  76, 79, 78, 81, 80, 83, 82, 85, 84, 87, 86, 89, 88, 91, 90, 93,
                  92, 95, 94, 97, 96, 99, 98, 101, 100, 103, 102, 105, 104, 107,
                  106, 109, 108, 111, 110, 113, 112, 115, 114, 117, 116, 119, 118,
                  121, 120, 123, 122, 125, 124, 127]

    tb16_master_divider = [-1, 255, 254, 253, 252, 251, 250, 249, 248, 247, 246,
                           245, 244, 243, 242, 241, 240, 239, 238, 237, 236, 235,
                           234, 233, 232, 231, 230, 229, 228, 227, 226, 225, 224,
                           223, 222, 221, 220, 219, 218, 217, 216, 215, 214, 213,
                           212, 211, 210, 209, 208, 207, 206, 205, 204, 203, 202,
                           201, 200, 199, 198, 197, 196, 195, 194, 193, 192, 128,
                           129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139,
                           140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150,
                           151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161,
                           162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172,
                           173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183,
                           184, 185, 186, 187, 188, 189, 191]

    tb16_slave_divider = [126, 124, 125, 122, 123, 120, 121, 118, 119, 116, 117,
                          114, 115, 112, 113, 110, 111, 108, 109, 106, 107, 104,
                          105, 102, 103, 100, 101, 98, 99, 96, 97, 94, 95, 92, 93,
                          90, 91, 88, 89, 86, 87, 84, 85, 82, 83, 80, 81, 78, 79, 76,
                          77, 74, 75, 72, 73, 70, 71, 68, 69, 66, 67, 64, 65, 1, 0, 3,
                          2, 5, 4, 7, 6, 9, 8, 11, 10, 13, 12, 15, 14, 17, 16, 19, 18,
                          21, 20, 23, 22, 25, 24, 27, 26, 29, 28, 31, 30, 33, 32, 35,
                          34, 37, 36, 39, 38, 41, 40, 43, 42, 45, 44, 47, 46, 49, 48,
                          51, 50, 53, 52, 55, 54, 57, 56, 59, 58, 61, 60, 63, 62, -1]

    tb16_master_tab_divider = [191, 189, 188, 187, 186, 185, 184, 183, 182, 181, 180,
                               179, 178, 177, 176, 175, 174, 173, 172, 171, 170, 169,
                               168, 167, 166, 165, 164, 163, 162, 161, 160, 159, 158,
                               157, 156, 155, 154, 153, 152, 151, 150, 149, 148, 147,
                               146, 145, 144, 143, 142, 141, 140, 139, 138, 137, 136,
                               135, 134, 133, 132, 131, 130, 129, 128, 192, 193, 194,
                               195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205,
                               206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216,
                               217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227,
                               228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238,
                               239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249,
                               250, 251, 252, 253, 254, 255, -1]

    tb16_slave_tab_divider = [126, 124, 125, 122, 123, 120, 121, 118, 119, 116, 117,
                              114, 115, 112, 113, 110, 111, 108, 109, 106, 107, 104,
                              105, 102, 103, 100, 101, 98, 99, 96, 97, 94, 95, 92, 93,
                              90, 91, 88, 89, 86, 87, 84, 85, 82, 83, 80, 81, 78, 79,
                              76, 77, 74, 75, 72, 73, 70, 71, 68, 69, 66, 67, 64, 65,
                              1, 0, 3, 2, 5, 4, 7, 6, 9, 8, 11, 10, 13, 12, 15, 14,
                              17, 16, 19, 18, 21, 20, 23, 22, 25, 24, 27, 26, 29, 28,
                              31, 30, 33, 32, 35, 34, 37, 36, 39, 38, 41, 40, 43, 42,
                              45, 44, 47, 46, 49, 48, 51, 50, 53, 52, 55, 54, 57, 56,
                              59, 58, 61, 60, 63, 62, -1]


class CalibFiles:
    '''APV calibration. To convert Volts to MIPs'''
    # path on alzt.tau.ac.il server = '/data/alzta/aborysov/tb_2016_data/code/lumical_clust/fcalib/'
    calib_files = ['./calibration_files/calibration_apv_0.txt', './calibration_files/calibration_apv_1.txt',
                   './calibration_files/calibration_apv_2.txt', './calibration_files/calibration_apv_3.txt',
                   './calibration_files/calibration_apv_4.txt', './calibration_files/calibration_apv_5.txt',
                   './calibration_files/calibration_apv_6.txt', './calibration_files/calibration_apv_7.txt',
                   './calibration_files/calibration_apv_8.txt', './calibration_files/calibration_apv_9.txt',
                   './calibration_files/calibration_apv_10.txt', './calibration_files/calibration_apv_11.txt',
                   './calibration_files/calibration_apv_12.txt', './calibration_files/calibration_apv_13.txt',
                   './calibration_files/calibration_apv_14.txt', './calibration_files/calibration_apv_15.txt']


class Hit:
    def __init__(self, apv_id, apv_channel, apv_signal):
        self.sector, self.pad, self.layer = self.position(apv_id, apv_channel)
        self.energy = self.calib_energy(apv_id, apv_signal)

        pos_align = 0
        # if self.layer == 0:
        #     pos_align = 0.1897
        # elif self.layer == 1:
        #     pos_align = -0.9405
        # elif self.layer > 1:
        #     pos_align = 0.7501

        self.rho = 80. + 0.9 + 1.8 * self.pad + pos_align
        self.phi = np.pi / 2 + np.pi / 12 - np.pi / 48 - np.pi / 24 * self.sector
        self.x = self.rho * np.cos(self.phi)
        self.y = self.rho * np.sin(self.phi)

    def position(self, apv_id, apv_channel):
        if apv_id < 4:
            apv_map = ApvMaps.tb15_slave if apv_id % 2 == 1 else ApvMaps.tb15_master

        elif apv_id >= 4 and apv_id < 14:
            apv_map = ApvMaps.tb16_slave_divider if apv_id % 2 == 1 else ApvMaps.tb16_master_divider

        elif apv_id == 14:
            apv_map = ApvMaps.tb16_master_tab_divider

        elif apv_id == 15:
            apv_map = ApvMaps.tb16_slave_tab_divider

        layer = apv_id // 2
        sector = apv_map[apv_channel] // 64
        pad = apv_map[apv_channel] % 64
        return sector, pad, layer

    def calib_energy(self, apv_id, apv_signal):
        calib_file = CalibFiles.calib_files[apv_id]

        x = [0.]
        y = [0. * 18.986]
        x_err = [1.e-5]
        y_err = [1.e-5 * 18.986]
        # Calibration x-y data is inverted
        # 18.6 comes from statement that mean of energy histo in layer2 should be the same as in MC
        with open(calib_file, 'r') as file:
            for line in islice(file, 1, None):
                x.append(float(line.split('  ')[1]))
                y.append(float(line.split('  ')[0]) * 18.986)  # ##18.61
                x_err.append(float(line.split('  ')[3]))
                y_err.append(float(line.split('  ')[2]) * 18.986)

        x = np.array(x)
        y = np.array(y)
        x_err = np.array(x_err)
        y_err = np.array(y_err)

        graph = TGraphErrors(len(x), x, y, x_err, y_err)

        signal = apv_signal if apv_signal < 1450. else 1450.

        return graph.Eval(signal)


class HitMC:
    def __init__(self, cell_id, energy_in_mev):
        mev2mip = 1. / 0.0885
        self.sector = ((int(cell_id) >> 8) & 0xff) - 11
        self.pad = int(cell_id) & 0xff
        self.layer = ((int(cell_id) >> 16) & 0xff) - 1
        self.energy = energy_in_mev * mev2mip

        # Implement noise in progress. Need to put not random number!
        self.energy = random.gauss(self.energy, 0.52353509)

        self.rho = 80. + 0.9 + 1.8 * self.pad
        self.phi = np.pi / 2 + np.pi / 12 - np.pi / 48 - np.pi / 24 * self.sector
        self.x = self.rho * np.cos(self.phi)
        self.y = self.rho * np.sin(self.phi)


class Tower:
    def __init__(self, tower_hits):
        self.hits = tower_hits

        self.sector = self.hits[0].sector
        self.pad = self.hits[0].pad

        self.energy = sum([hit.energy for hit in self.hits])

        self.neighbor = -1
        self.cluster = -1


class Cluster:
    def __init__(self, cluster_hits, cluster_towers, det):
        self.hits = cluster_hits
        self.towers = cluster_towers
        self.det = det

        self.energy = self.get_energy()

        # Energies in trackers. LogW in Calorimeter
        self.weights = self.get_weights()

        self.pad = self.get_position('pad')
        self.sector = self.get_position('sector')
        self.layer = self.get_position('layer')
        self.rho = self.get_position('rho')
        self.x = self.get_position('x')
        self.y = self.get_position('y')

        self.n_pads = self.get_n_pads()

    def get_energy(self):
        return sum([hit.energy for hit in self.hits])

    def get_weights(self):
        if self.det == 'Cal':
            w0 = 3.4
            return [max(0, w0 + np.log(hit.energy / self.energy)) for hit in self.hits]
        else:
            return [hit.energy for hit in self.hits]

    def get_position(self, pos_string):
        if sum(self.weights) == 0:
            return -9999
        positions = [getattr(hit, pos_string) for hit in self.hits]
        return sum([pos * self.weights[idx] / sum(self.weights) for idx, pos in enumerate(positions)])

    def get_n_pads(self):
        return len(self.hits)

    def merge(self, cluster2):
        self.hits += cluster2.hits
        for tower2 in cluster2.towers:
            tower2.cluster = self.towers[0].cluster
        self.towers += cluster2.towers
        self.energy = self.get_energy()
        self.weights = self.get_weights()

        self.pad = self.get_position('pad')
        self.sector = self.get_position('sector')
        self.layer = self.get_position('layer')
        self.rho = self.get_position('rho')
        self.x = self.get_position('x')
        self.y = self.get_position('y')

        self.n_pads = self.get_n_pads()


def set_towers(hits):
    towers_pos = set([(hit.sector, hit.pad) for hit in hits])
    towers = []
    for pos in towers_pos:
        tower_hits = [hit for hit in hits if (hit.sector, hit.pad) == pos]
        towers.append(Tower(tower_hits))

    towers.sort(key=lambda x: x.energy, reverse=True)

    return towers


def set_neighbors(towers):
    for tower in towers:
        most_energetic_neighbor = tower

        for tower_neighbor in towers:
            if (tower_neighbor.sector in range(tower.sector - 1, tower.sector + 2)
               and tower_neighbor.pad in range(tower.pad - 1, tower.pad + 2)):
                most_energetic_neighbor = tower_neighbor if tower_neighbor.energy >= most_energetic_neighbor.energy else most_energetic_neighbor

        tower.neighbor = most_energetic_neighbor


def set_tower_clusters(towers):
    cluster_idx = 0
    for tower in towers:
        if (tower.neighbor.sector, tower.neighbor.pad) == (tower.sector, tower.pad):
            tower.cluster = cluster_idx
            cluster_idx += 1

    n_non_clusters = -1
    while n_non_clusters != 0:
        n_non_clusters = 0
        for tower in towers:
            if tower.cluster == -1:
                n_non_clusters += 1
                if tower.neighbor.cluster != -1:
                    tower.cluster = tower.neighbor.cluster


def merge_clusters(clusters):
    restart = True
    while restart:
        for idx1, cluster1 in enumerate(clusters):
            for idx2, cluster2 in enumerate(clusters):
                if cluster1 != cluster2:
                    distance = abs(cluster1.y - cluster2.y)
                    ratio = cluster2.energy / cluster1.energy
                    if distance < 9. or (distance < 36. and ratio < 0.1 - 0.1 / 20 * distance):
                        cluster1.merge(cluster2)
                        clusters.remove(cluster2)
                        break
            else:
                continue
            break
        else:
            restart = False


def set_clusters(towers, det):
    clusters = []

    if len(towers) == 0:
        return clusters

    set_neighbors(towers)
    set_tower_clusters(towers)

    n_clusters = max([tower.cluster for tower in towers]) + 1
    for cluster in range(n_clusters):
        cluster_hits = []
        cluster_towers = []
        for tower in towers:
            if tower.cluster == cluster:
                cluster_hits.extend(tower.hits)
                cluster_towers.append(tower)
        clusters.append(Cluster(cluster_hits, cluster_towers, det))

    clusters.sort(key=lambda x: x.energy, reverse=True)

    for i, cluster in enumerate(clusters):
        for tower in cluster.towers:
            tower.cluster = i

    merge_clusters(clusters)

    clusters.sort(key=lambda x: x.energy, reverse=True)

    for i, cluster in enumerate(clusters):
        for tower in cluster.towers:
            tower.cluster = i

    return clusters


def langaufun(x, par):
    invsq2pi = 0.3989422804014  # (2 pi)^(-1 / 2)
    mpshift = -0.22278298  # Landau maximum location

    np = 1000  # number of convolution steps
    sc = 5.  # convolution extends to +-sc Gaussian sigmas

    summ = 0

    mpc = par[1] - mpshift * par[0]

    xlow = x[0] - sc * par[3]
    xupp = x[0] + sc * par[3]

    step = (xupp - xlow) / np

    if par[0] == 0:
        par[0] = 1e-6
    if par[3] == 0:
        par[3] = 1e-6
    for i in range(np // 2):
        xx = xlow + (i + 0.5) * step
        fland = TMath.Landau(xx, mpc, par[0]) / par[0]
        summ += fland * TMath.Gaus(x[0], xx, par[3])

        xx = xupp - (i + 0.5) * step
        fland = TMath.Landau(xx, mpc, par[0]) / par[0]
        summ += fland * TMath.Gaus(x[0], xx, par[3])

    return par[2] * step * summ * invsq2pi / par[3]


def bad_pad(sector, pad, layer):
    return ((layer == 0 and sector == 1 and pad in (26, 61))
            or (layer == 0 and sector == 2 and pad in (31, 57, 61))
            or (layer == 2 and sector == 1 and pad in (28, 31, 34))
            or (layer == 2 and sector == 2 and pad in (38, 53))
            or (layer == 3 and sector == 2 and pad in (31, 33, 52, 55, 61))
            or (layer == 4 and sector == 1 and pad in (29, 39, 41, 55, 56))
            or (layer == 4 and sector == 2 and pad in (28,))
            or (layer == 5 and sector == 1 and pad in (32, 36, 40, 41, 44, 45, 49, 56, 58))
            or (layer == 5 and sector == 2 and pad in (28, 52, 54, 61))
            or (layer == 6 and sector == 1 and pad in (26, 30))
            or (layer == 6 and sector == 2 and pad in (34, 42, 54, 57, 59, 60)))
