import os
import argparse
import numpy as np
import matplotlib.pyplot as plt


parser = argparse.ArgumentParser()
parser.add_argument('-d', '--dir', metavar='Topology file', type=str, dest='dir',
                    default=os.path.join(os.curdir, 'buffersize_test_google_resnet_fwd'),
                    help="Path to the topology file")
args = parser.parse_args()
test_dir = args.dir


filelist = list(os.listdir(test_dir))
fileprefix = f"{'_'.join(filelist[0].split('_')[:-1])}_"
bflist = np.array(sorted(list(map(lambda x: int(x.split('_')[-1]), filelist))))
total_cycles   = []
stall_cycles   = []
overall_utils  = []
map_efficiency = []
compute_utils  = []


for bf in bflist:
    with open(os.path.join(test_dir, fileprefix + str(bf), 'COMPUTE_REPORT.csv'), 'rt') as file:
        content = list(map(lambda x: x.split(','), file.readlines()[1:]))
        total_cycles.append(np.sum(np.array(list(map(lambda x: float(x[1].strip()), content)))))
        stall_cycles.append(np.sum(np.array(list(map(lambda x: float(x[2].strip()), content)))))
        overall_utils.append(np.average(np.array(list(map(lambda x: float(x[3].strip()), content)))))
        map_efficiency.append(np.average(np.array(list(map(lambda x: float(x[4].strip()), content)))))
        compute_utils.append(np.average(np.array(list(map(lambda x: float(x[5].strip()), content)))))


x_axis = np.arange(len(bflist))
y_axis = np.array(total_cycles)
plt.bar(x_axis, y_axis, width=0.2)
# for i, j in zip(x_axis, y_axis):
#     plt.annotate(f"{j:.0f}", xy=(i, j), ha='center')
plt.xticks(x_axis, bflist, rotation=0, ha='center')
# plt.ylim([0, 1.1])

plt.title('Buffer size test result')
plt.xlabel('Size of SRAM buffer (kB)')
plt.ylabel('stall cycles (ratio)')
plt.tight_layout()
plt.show()