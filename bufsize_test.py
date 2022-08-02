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
                        default='auto',
                        help="Path to log dir"
                        )

    args = parser.parse_args()
    topology = args.t
    temppath = args.c
    logpath = args.p
    if logpath == 'auto':
        logpath = os.path.join(os.curdir, 'test_runs',
                               f'bandwidth_test_'
                               f'{temppath.split(os.sep)[-1].split(".")[0]}_'
                               f'{topology.split(os.sep)[-1].split(".")[0]}')

    os.makedirs(logpath, exist_ok=True)

    buffsizes = [2, 8, 32, 128, 512, 2048, 4096, 6144]

    for bf in buffsizes:
        config = configparser.ConfigParser()
        config.read(temppath)
        config['general']['run_name'] = '_'.join([config['general']['run_name'], f"bf_{bf}"])
        config['architecture_presets']['IfmapSramSzkB'] = str(bf)
        config['architecture_presets']['FilterSramSzkB'] = str(bf)
        config['architecture_presets']['OfmapSramSzkB'] = str(bf)
        config['run_presets']['InterfaceBandwidth'] = 'USER'
        
        config_filepath = os.path.join(os.curdir, 'configs', '.'.join([config['general']['run_name'], 'cfg']))
        with open(config_filepath, 'wt') as file:
            config.write(file)

        s = scalesim(save_disk_space=True, verbose=True,
                 config=config_filepath,
                 topology=topology,
                 )
        s.run_scale(top_path=logpath)
