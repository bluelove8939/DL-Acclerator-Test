import os
import argparse
import numpy as np
import matplotlib.pyplot as plt


parser = argparse.ArgumentParser()
parser.add_argument('-d', '--dir', metavar='Topology file', type=str, dest='dir',
                    default=os.path.join(os.curdir, 'bandwidth_test_google_resnet_fwd'),
                    help="Path to the topology file")
args = parser.parse_args()
test_dir = args.dir


filelist = list(os.listdir(test_dir))
fileprefix = f"{'_'.join(filelist[0].split('_')[:-1])}_"
bwlist = np.array(sorted(list(map(lambda x: int(x.split('_')[-1]), filelist))))
total_cycles   = []
stall_cycles   = []
overall_utils  = []
map_efficiency = []
compute_utils  = []


for bw in bwlist:
    with open(os.path.join(test_dir, fileprefix + str(bw), 'COMPUTE_REPORT.csv'), 'rt') as file:
        content = list(map(lambda x: x.split(','), file.readlines()[1:]))
        total_cycles.append(np.average(np.array(list(map(lambda x: float(x[1].strip()), content)))))
        stall_cycles.append(np.average(np.array(list(map(lambda x: float(x[2].strip()), content)))))
        overall_utils.append(np.average(np.array(list(map(lambda x: float(x[3].strip()), content)))))
        map_efficiency.append(np.average(np.array(list(map(lambda x: float(x[4].strip()), content)))))
        compute_utils.append(np.average(np.array(list(map(lambda x: float(x[5].strip()), content)))))


x_axis = np.arange(len(bwlist))
print(stall_cycles)
plt.bar(x_axis, np.array(stall_cycles) / np.array(total_cycles), width=0.2)
plt.xticks(x_axis, bwlist, rotation=0, ha='center')

plt.title('Bandwidth test result')
plt.xlabel('Bandwidth (word/cycles)')
plt.ylabel('stall cycles (ratio)')
plt.tight_layout()
plt.show()