'''
This file does analysis of cluster reconstruction in calorimeter and trackers
signals in coresponded functions cluster_analysis(), tracker_analysis().
To start this script user needs all imported libraries. Python3 with root.
P.S. It may work with python2. But it may HAVE BUGS!!! Because in python2:
1/2=0, when in python3 1/2=0.5 and so on... + python2 slower x4 times. So adapt
to use python3. You will need ROOT with python3. If it works only with python2
but not python3. You have to reinstall it and compile source (dont use binary)
with python3 executable/library/include paths provided in ./configure stage.
Include directory for me was tricky: /path/to/python/include/python3.7m. So
play
round it.
'''

from ROOT import TH1F, TH2F, TF1, TGraphErrors, TFile, gROOT, TCanvas, gStyle
import time
import numpy as np

from variables import n_sectors, n_pads, apv_maps, calib_path, \
    calib_file_names, langaufun

# To measure time of execution
start_time = time.time()

# Dont draw pictures in the end
gROOT.SetBatch(1)
# Dont draw statistics of histograms
gStyle.SetOptStat(0)


class tower():
    def __init__(self, position, energy):
        self.position = position
        self.energy = energy
        self.neighbor_position = -1
        self.neighbor_cluster = -1
        self.cluster = -1


class AnalizeCalorimeterEvent(object):
    def __init__(self, filename):
        # Create root file and open "filename" file
        self.file = TFile.Open(filename)

        # Read a TTree from this file
        self.tree = self.file.apv_reco

        # Create dictionary for all histograms
        self.h_dict = {}

    # Special methods for losers
    def __getitem__(self, key):
        return getattr(self, key)

    # Primary methods
    def extract_data(self, event):
        '''
        This method extracts data from ROOT file. Applies cuts on data and
        saves it as 2d array for each event.
        '''

        self.towers_list = []

        # Read all branches from the input ROOT file.
        id_arr = event.apv_id
        channel_arr = event.apv_ch
        signal_arr = event.apv_signal_maxfit
        apv_nn_output = event.apv_nn_output
        apv_fit_tau = event.apv_fit_tau
        apv_fit_t0 = event.apv_fit_t0
        apv_bint1 = event.apv_bint1

        # Make local variables to improve speed
        # Method calculates position of the signal
        position = self.position
        # Method calculated energy of the signal
        calib_energy = self.calib_energy
        # 2d array to save data
        towers_list = self.towers_list

        # Loop through all signals in the event
        for hit in range(len(id_arr)):
            # Calculate position of the signal
            sector, pad, layer = position(id_arr[hit], channel_arr[hit])

            # Cuts. Analize only calorimeter, do geometry cuts and bad mapping cut
            if (layer < 2
               or sector == 0 or sector == 4
               or (sector == 1 and pad < 20)
               or pad < 0
                # More cuts. it was ctrl+c ctrl+v from Sasha's code.
               or apv_fit_tau[hit] < 1 or apv_fit_tau[hit] > 3
               or signal_arr[hit] > 2000 or signal_arr[hit] < 0.75
               or apv_nn_output[hit] < 0.5
               or apv_fit_t0[hit] < (apv_bint1[hit]-2.7)
               or apv_fit_t0[hit] > (apv_bint1[hit]-0.5)):
                continue

            # Calculate energy of the event and write it in 2d array
            energy = calib_energy(id_arr[hit], signal_arr[hit])
            if energy < 0:
                return 0
            for item in towers_list:
                if item.position == (sector, pad):
                    item.energy += energy
                    break
            else:
                towers_list.append(tower((sector, pad), energy))

            self.towers_list = towers_list
        return 1

    def clustering_in_towers(self, merging='on'):
        '''
        This method does clustering to the input data - 2d array.
        '''

        # Optimization
        towers_list = self.towers_list
        # merge_clusters = self.merge_clusters

        for item in towers_list:
            center_sec, center_pad = item.position
            neighbors = []
            for item_neighbor in towers_list:
                if (item_neighbor.position[0] in range(center_sec-1, center_sec+2)
                   and item_neighbor.position[1] in range(center_pad-1, center_pad+2)):
                    neighbors.append(item_neighbor)
            neighbors_sorted = sorted(neighbors, key=lambda x: x.energy, reverse=True)

            item.neighbor = neighbors_sorted[0]

        towers_list = sorted(towers_list, key=lambda x: x.energy, reverse=True)
        cluster_idx = 0
        for item in towers_list:
            if item.neighbor.position == item.position:
                item.cluster = cluster_idx
                cluster_idx += 1

        n_non_clusters = -1
        while n_non_clusters != 0:
            n_non_clusters = 0
            for item in towers_list:
                if item.cluster == -1:
                    n_non_clusters += 1
                    if item.neighbor.cluster != -1:
                        item.cluster = item.neighbor.cluster

        self.towers_list = towers_list

        # if merging == 'on':
        #    for cluster in range(amax(clusters_arr)):
        #        merge_clusters(cluster, cluster+1)

    #def merge_clusters(self, cluster1, cluster2):
    #    clusters_arr = self.clusters_arr

    #    if not ((clusters_arr == cluster1).any()
    #       and (clusters_arr == cluster2).any()):
    #        pass
    #    elif (self.get_sector_distance(cluster1, cluster2) < 1.5
    #          and self.get_pad_distance(cluster1, cluster2) < 4.5):
    #            # Make 0 cluster 1st, and then substarct 1
    #        clusters_arr[clusters_arr == cluster1] = cluster2
    #        for sec in range(n_sectors):
    #            for pad in range(n_pads):
    #                if clusters_arr[sec, pad] >= cluster2:
    #                    clusters_arr[sec, pad] -= 1
    #        self.merge_clusters(cluster1, cluster2)
    #    else:
    #        self.merge_clusters(cluster1, cluster2+1)

    def PlotCheck(self, event):
        h_key = 'check_event_{}'.format(event.apv_evt)
        h_dict = self.h_dict
        try:
            for item in self.towers_list:
                h_dict[h_key].Fill(item.position[0], item.position[1], item.energy)
        except KeyError:

            h_dict[h_key] = TH2F(h_key, '', 6, 0, 6, 64, 0, 64)
            h_dict[h_key].SetTitle('event_{};sector;pad'.format(event.apv_evt))
            for item in self.towers_list:
                h_dict[h_key].Fill(item.position[0], item.position[1], item.energy)

        c1 = TCanvas('c1', h_key, 1800, 1800)
        h_dict[h_key].Draw("COLZTEXT")

        c1.Print('./checks/'+h_key+'.png')

    def FillNclusters(self):
        h_key = 'h_n_clusters'
        h_dict = self.h_dict
        try:
            h_dict[h_key].Fill(self.get_n_clusters())
        except KeyError:
            h_dict[h_key] = TH1F(h_key, '', 15, 0, 15)
            h_dict[h_key].SetTitle('N clusters;N Clusters;N Events')
            h_dict[h_key].Fill(self.get_n_clusters())

    def FillClusterEnergy(self, cluster):
        for item in self.towers_list:
            if item.cluster == cluster:
                break
        else:
            return 0

        h_dict = self.h_dict
        h_key = 'h_energy_{}'.format(cluster+1)
        try:
            h_dict[h_key].Fill(self.get_cluster_energy(cluster))
        except KeyError:
            h_dict[h_key] = TH1F(h_key, '', 2000, 0, 500)
            h_dict[h_key].SetTitle('Energy: {} clust;Energy [MIP];N events'.format(cluster+1))
            h_dict[h_key].Fill(self.get_cluster_energy(cluster))

    def Fill1PadEnergy(self):
        h_dict = self.h_dict
        get_cluster_n_pads = self.get_cluster_n_pads
        get_cluster_energy = self.get_cluster_energy
        h_key = 'h_energy_1pad'
        try:
            for cluster in range(self.get_n_clusters()):
                if get_cluster_n_pads(cluster) == 1:
                    h_dict[h_key].Fill(get_cluster_energy(cluster))
        except KeyError:
            h_dict[h_key] = TH1F(h_key, '', 2000, 0, 100)
            h_dict[h_key].SetTitle('Energy: 1 pad clusters;Energy [MIP];N events')
            for cluster in range(self.get_n_clusters()):
                if get_cluster_n_pads(cluster) == 1:
                    h_dict[h_key].Fill(get_cluster_energy(cluster))

    def FillClusterPadPos(self, cluster):
        for item in self.towers_list:
            if item.cluster == cluster:
                break
        else:
            return 0
        h_dict = self.h_dict
        h_key = 'h_position_{}'.format(cluster+1)
        try:
            h_dict[h_key].Fill(self.get_cluster_pad_pos(cluster))
        except KeyError:
            h_dict[h_key] = TH1F(h_key, '', 200, 0, 64)
            h_dict[h_key].SetTitle('Position: {} cluster;pos [pad];N events'.format(cluster+1))
            h_dict[h_key].Fill(self.get_cluster_pad_pos(cluster))

    def FillClusterNPads(self, cluster):
        for item in self.towers_list:
            if item.cluster == cluster:
                break
        else:
            return 0
        h_dict = self.h_dict
        h_key = 'h_npads_{}'.format(cluster+1)
        try:
            h_dict[h_key].Fill(self.get_cluster_n_pads(cluster))
        except KeyError:
            h_dict[h_key] = TH1F(h_key, '', 25, 0, 25)
            h_dict[h_key].SetTitle('N pads: {} cluster;N pads;N events'.format(cluster+1))
            h_dict[h_key].Fill(self.get_cluster_n_pads(cluster))

    def FillClusterDistance(self, cluster1, cluster2):
        ok1, ok2 = 0, 0
        for item in self.towers_list:
            if item.cluster == cluster1:
                ok1 = 1
            elif item.cluster == cluster2:
                ok2 = 1
            if ok1 == 1 and ok2 == 1:
                break
        else:
            return 0
        h_dict = self.h_dict
        h_key = 'h_distance_{}_vs_{}'.format(cluster1+1, cluster2+1)
        try:
            h_dict[h_key].Fill(self.get_pad_distance(cluster1, cluster2))
        except KeyError:
            h_dict[h_key] = TH1F(h_key, '', 400, 0, 60)
            self.h_dict[h_key].SetTitle('Distance between: {} and {} clusters;N pads;\
                                            N events'.format(cluster1+1, cluster2+1))
            h_dict[h_key].Fill(self.get_pad_distance(cluster1, cluster2))

    def FillClusterRatio(self, cluster1, cluster2):
        ok1, ok2 = 0, 0
        for item in self.towers_list:
            if item.cluster == cluster1:
                ok1 = 1
            elif item.cluster == cluster2:
                ok2 = 1
            if ok1 == 1 and ok2 == 1:
                break
        else:
            return 0
        h_dict = self.h_dict
        h_key = 'h_ratio_{}_over_{}'.format(cluster2+1, cluster1+1)
        try:
            h_dict[h_key].Fill(self.get_energy_ratio(cluster1, cluster2))
        except KeyError:
            h_dict[h_key] = TH1F(h_key, '', 400, 0, 1)
            h_dict[h_key].SetTitle('Energy ratio: {} over {} clusters;Ratio;\
                                    N events'.format(cluster2+1, cluster1+1))
            h_dict[h_key].Fill(self.get_energy_ratio(cluster1, cluster2))

    def FillClusterInverseRatio(self, cluster1, cluster2):
        ok1, ok2 = 0, 0
        for item in self.towers_list:
            if item.cluster == cluster1:
                ok1 = 1
            elif item.cluster == cluster2:
                ok2 = 1
            if ok1 == 1 and ok2 == 1:
                break
        else:
            return 0
        h_dict = self.h_dict
        h_key = 'h__inverse_ratio_{}_over_{}'.format(cluster2+1, cluster1+1)
        try:
            h_dict[h_key].Fill(1/self.get_energy_ratio(cluster1, cluster2))
        except KeyError:
            h_dict[h_key] = TH1F(h_key, '', 400, 0, 200)
            h_dict[h_key].SetTitle('Inverse Energy ratio: {} over {} clusters;Ratio;\
                                    N events'.format(cluster2+1, cluster1+1))
            h_dict[h_key].Fill(1/self.get_energy_ratio(cluster1, cluster2))

    def FillClusterDistVsRatio(self, cluster1, cluster2):
        ok1, ok2 = 0, 0
        for item in self.towers_list:
            if item.cluster == cluster1:
                ok1 = 1
            elif item.cluster == cluster2:
                ok2 = 1
            if ok1 == 1 and ok2 == 1:
                break
        else:
            return 0
        h_dict = self.h_dict
        h_key = 'h_dist_ratio_for_{}_and_{}'.format(cluster1+1, cluster2+1)
        try:
            h_dict[h_key].Fill(self.get_pad_distance(cluster1, cluster2),
                               self.get_energy_ratio(cluster1, cluster2))
        except KeyError:
            h_dict[h_key] = TH2F(h_key, '', 400, 0, 60, 400, 0, 1)
            h_dict[h_key].SetTitle('Distance vs ratio: {} and {} clusters;Distance;\
                                    Ratio;N Events'.format(cluster1+1, cluster2+1))
            h_dict[h_key].Fill(self.get_pad_distance(cluster1, cluster2),
                               self.get_energy_ratio(cluster1, cluster2))

    # Secondary methods
    def position(self, apv_id, apv_channel):

        '''
        Input: APV's id and channel
        Output:Tuple (sector, pad, layer): APV position in the detector
        Does: Read mapping array. Returns pad id and sector position of APV.
        Schematicaly pad ids and sectors numbering you can see in variables.py.
        '''

        # APV_id: odd - slave, even - master
        if apv_id < 4:
            if apv_id % 2 == 1:
                map_name = 'tb15_slave'
            else:
                map_name = 'tb15_master'
        elif apv_id >= 4 and apv_id < 14:
            if apv_id % 2 == 1:
                map_name = 'tb16_slave_divider'
            else:
                map_name = 'tb16_master_divider'
        elif apv_id == 14:
            map_name = 'tb16_master_tab_divider'
        elif apv_id == 15:
            map_name = 'tb16_slave_tab_divider'

        # Calculate corresponded position
        sector = apv_maps[map_name][apv_channel]//n_pads
        pad = apv_maps[map_name][apv_channel] % n_pads
        layer = apv_id//2

        return sector, pad, layer

    def calib_energy(self, apv_id, apv_signal):
        '''
        Input:APV's id and signal(fit of RC-CR function) in MIPs.
        Output:Energy deposited in the layer
        Does: Reads calibration data files. Creates TGraphError with this data.
        Returns interpolated energy value - apv_energy
        '''
        # Optimization
        array = np.array

        # Calibration only to 1450 signal. No extrapolation. Just cut
        signal_treshold = 1450.
        cal_path = calib_path
        cal_file_name = calib_file_names[apv_id]

        # First point of callibraion curve
        x = [0.]
        y = [0.*16.5*1.164]
        x_err = [1.e-5]
        y_err = [1.e-5*16.5*1.164]

        # Calibration data in file written as (x,y,x_err,y_err) for each APV_id
        with open('%(cal_path)s%(cal_file_name)s' % locals(), 'r') as file:
            for i, line in enumerate(file):

                # skip a line with a title
                if i == 0:
                    continue

                # Calibration x-y data is inverted
                x.append(float(line.split('  ')[1]))
                y.append(float(line.split('  ')[0])*16.5*1.164)
                x_err.append(float(line.split('  ')[3]))
                y_err.append(float(line.split('  ')[2])*16.5*1.164)

        x = array(x)
        y = array(y)
        x_err = array(x_err)
        y_err = array(y_err)

        graph = TGraphErrors(len(x), x, y, x_err, y_err)

        # Copypasted from Sasha's code. Scale calibration graphs
        # Normalization D/MC according to L2 *1.09# /4.3 divide when No CD
        # for point in range(graph.GetN()):
            # Scale Y to get MIPS
        #    graph.GetY()[point] *= 16.5*1.164

            # y_err zero anyway
        #    graph.GetEY()[point] *= 16.5*1.164

        # Take into account threshold
        if apv_signal > signal_treshold:
            signal = signal_treshold
        else:
            signal = apv_signal

        return graph.Eval(signal)

    # Get functions

    def get_n_clusters(self):
        cluster_list = [item.cluster for item in self.towers_list]
        if not cluster_list:
            return 0
        return max(cluster_list)+1

    def get_cluster_energy(self, cluster):
        energy_list = [item.energy for item in self.towers_list if item.cluster == cluster]
        # If no cluster returns 0
        return sum(energy_list)

    def get_cluster_pad_pos(self, cluster):

        cluster_pos = 0
        cluster_energy = self.get_cluster_energy(cluster)
        pos_energy_list = [(item.position[1], item.energy) for item in self.towers_list if item.cluster == cluster]

        for pos_energy in pos_energy_list:
            cluster_pos += pos_energy[0]*pos_energy[1]/cluster_energy
        # if no cluster returns 0 pos
        return cluster_pos

    def get_cluster_sector_pos(self, cluster):

        cluster_pos = 0
        cluster_energy = self.get_cluster_energy(cluster)
        pos_energy_list = [(item.position[0], item.energy) for item in self.towers_list if item.cluster == cluster]

        for pos_energy in pos_energy_list:
            cluster_pos += pos_energy[0]*pos_energy[1]/cluster_energy
        # if no cluster returns 0 pos
        return cluster_pos

    def get_cluster_n_pads(self, cluster):
        n_pads_list = [item for item in self.towers_list if item.cluster == cluster]
        # Returns 0 if no clusters
        return len(n_pads_list)

    def get_pad_distance(self, cluster1, cluster2):
        get_cluster_pad_pos = self.get_cluster_pad_pos
        position1 = get_cluster_pad_pos(cluster1)
        position2 = get_cluster_pad_pos(cluster2)
        # This is only projection on pad distance!
        return abs(position1-position2)

    def get_sector_distance(self, cluster1, cluster2):
        get_cluster_sector_pos = self.get_cluster_sector_pos
        position1 = get_cluster_sector_pos(cluster1)
        position2 = get_cluster_sector_pos(cluster2)
        # This is only projection on sector distance!
        return abs(position1-position2)

    def get_energy_ratio(self, cluster1, cluster2):
        get_cluster_energy = self.get_cluster_energy
        energy1 = get_cluster_energy(cluster1)
        energy2 = get_cluster_energy(cluster2)
        return energy2/energy1


def tracker_analysis(tracker_layer):
    '''
    Calculates next variables for a tracker layer: Number of hits,
    total energy deposited, positions of hits. Plots histograms.
    '''

    gROOT.SetBatch(1)
    # gStyle.SetOptStat(0)

    input_filename = 'run741_tb16_charge_div_nn_reg9_nocm_corr_wfita_reco.root'
    input_file = TFile.Open(input_filename)

    h_energy_calib = TH1F('h_energy_calib', '', 100, 0, 10.)
    h_energy_calib.SetTitle('Total energy per event;Energy, [MIP];N events')

    h_position = TH1F('h_position', '', 64, 0-0.5, 64-0.5)
    h_position.SetTitle('Position per hit;Pad number;N events')

    h_n_hits = TH1F('h_hits_number', '', 5, 0-0.5, 5-0.5)
    h_n_hits.SetTitle('N Hits per event;N hits;N events')

    for idx, event in enumerate(input_file.apv_reco):
        # Use to debug to pass not all 50k points
        if idx == 200:
            break

        n_events = input_file.apv_reco.GetEntries()
        if idx == 0:
            print('Evaluating', n_events, 'Events:')

        if idx % (n_events*2//100) == 0:
            print(tracker_layer, 'Tracker:', end=' ')
            print(100*idx//n_events, '% are done', end=' ')
            print('Time used:', (time.time()-start_time)//60, 'min', end=' ')
            print(int((time.time()-start_time)) % 60, 'sec')

        n_hits = 0
        energy = 0.

        id_arr = event.apv_id
        channel_arr = event.apv_ch
        signal_arr = event.apv_signal_maxfit

        for j in range(len(id_arr)):

            sector, pad, layer = position(id_arr[j], channel_arr[j])

            # ###Start of cut section###
            # Cut on APV maping
            if pad < 0:
                continue
            # Geometry cuts
            if not (sector == 1 or sector == 2):
                continue
            # Cut on APV noisy area
            if sector == 1 and pad < 20:
                continue

            # Analyse only defined trackers
            if layer != tracker_layer:
                continue

            # More cuts. it was ctrl+c ctrl+v from Sasha's code.
            cond_1 = event.apv_fit_tau[j] > 1. and event.apv_fit_tau[j] < 3.
            cond_2 = signal_arr[j] < 2000.
            cond_31 = layer < 2 and signal_arr[j] > 0.
            cond_32 = event.apv_nn_output[j] > 0.5
            cond_41 = layer >= 2 and signal_arr[j] > 0.75
            cond_42 = event.apv_nn_output[j] > 0.5
            cond_51 = event.apv_fit_t0[j] > (event.apv_bint1[j]-2.7)
            cond_52 = event.apv_fit_t0[j] < (event.apv_bint1[j]-0.5)

            if not (cond_1 and cond_2
               and ((cond_31 and cond_32) or (cond_41 and cond_42))
               and cond_51 and cond_52):
                continue

            # ###End of cut section###

            n_hits += 1
            energy += calib_energy(id_arr[j], signal_arr[j])

            h_position.Fill(pad)

        h_energy_calib.Fill(energy)
        h_n_hits.Fill(n_hits)

    output_file = TFile('output.root', 'update')

    h_energy_calib.Write('energy_tracker_'+str(tracker_layer))
    h_position.Write('position_tracker_'+str(tracker_layer))
    h_n_hits.Write('hits_tracker_'+str(tracker_layer))

    output_file.Close()


def energy_fit(tracker_layer):
    file = TFile('output.root', 'read')
    # Landau-Gauss fitting:
    fit_function = TF1('fit_function', langaufun, 0.1, 6, 4)
    fit_function.SetNpx(300)

    # Starting parameters
    fit_function.SetParameters(0.5, 1., 2600., 0.1)
    fit_function.SetParNames('Width', 'MP', 'Area', 'GSigma')

    print('It tries to fit. Please be pation and make yourself a tea :3')

    histo = file.Get('energy_tracker_'+str(tracker_layer))
    histo.SetTitle('Total Energy per event: Tracker '+str(tracker_layer))

    histo.Fit('fit_function', "R")  # fit within specified range
    histo.Draw()

    print('Time used:', int(time.time()-start_time)//60, 'min ', end=' ')
    print(int(time.time()-start_time) % 60, 'sec')

    input('Pause. Enter a digit to exit')


def main():
    filename = './trees/run741_tb16_charge_div_nn_reg9_nocm_corr_wfita_reco.root'
    Analizer = AnalizeCalorimeterEvent(filename)
    n_events = Analizer.tree.GetEntries()

    for idx, event in enumerate(Analizer.tree):
        #if idx == 2000:
        #    break

        if idx % (300) == 0:
            time_min = (time.time()-start_time) // 60
            time_sec = (time.time()-start_time) % 60
            print('%(idx)i/%(n_events)i events' % locals(), end=' ')
            print('%(time_min)i min' % locals(), end=' ')
            print('%(time_sec)i sec' % locals())

        check = Analizer.extract_data(event)
        if check == 0:
            continue

        # Analizer.PlotCheck(event)

        Analizer.clustering_in_towers(merging='off')

        Analizer.Fill1PadEnergy()

        Analizer.FillNclusters()
        for cluster in range(1, 4):
            Analizer.FillClusterDistance(0, cluster)
            Analizer.FillClusterRatio(0, cluster)
            Analizer.FillClusterDistVsRatio(0, cluster)

        for cluster in range(0, 4):
            Analizer.FillClusterEnergy(cluster)
            Analizer.FillClusterPadPos(cluster)
            Analizer.FillClusterNPads(cluster)

    output_file = TFile('output_new.root', 'update')

    for key in Analizer.h_dict.keys():
        Analizer.h_dict[key].Write()

    input('Wait')


main()
