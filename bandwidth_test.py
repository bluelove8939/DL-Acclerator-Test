import os
import argparse
import configparser

from scalesim.scale_sim import scalesim

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', metavar='Topology file', type=str,
                        default=os.path.join(os.curdir, 'topologies', 'conv_nets', 'alexnet.csv'),
                        help="Path to the topology file"
                        )
    parser.add_argument('-c', metavar='Config file', type=str,
                        default=os.path.join(os.curdir, 'configs', 'google.cfg'),
                        help="Path to the config file"
                        )
    parser.add_argument('-p', metavar='log dir', type=str,
                        default=os.path.join(os.curdir, 'test_runs', 'bandwidth_test'),
                        help="Path to log dir"
                        )

    args = parser.parse_args()
    topology = args.t
    temppath = args.c
    logpath = args.p

    os.makedirs(logpath, exist_ok=True)

    bandwidths = [64, 128, 256, 512]

    for bw in bandwidths:
        config = configparser.ConfigParser()
        config.read(temppath)
        config['general']['run_name'] = '_'.join([config['general']['run_name'], f"bw_{bw}"])
        config['architecture_presets']['Bandwidth'] = str(bw)
        config['run_presets']['InterfaceBandwidth'] = 'USER'
        
        config_filepath = os.path.join(os.curdir, 'configs', '.'.join([config['general']['run_name'], 'cfg']))
        with open(config_filepath, 'wt') as file:
            config.write(file)

        s = scalesim(save_disk_space=True, verbose=True,
                 config=config_filepath,
                 topology=topology,
                 )
        s.run_scale(top_path=logpath)
