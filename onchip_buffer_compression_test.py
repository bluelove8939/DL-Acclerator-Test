import os
import argparse
import configparser
import math

from scalesim.scale_sim import scalesim


parser = argparse.ArgumentParser(description='On-Chip Buffer Compression Test Configs')
parser.add_argument('-tp', '--topology', default=os.path.join(os.curdir, 'topologies', 'conv_nets', 'alexnet.csv'), type=str,
                    help='Topology file path', dest='topo_path')
parser.add_argument('-cf', '--configs', default=os.path.join(os.curdir, 'configs', 'google.cfg'), type=str,
                    help='Accelerator configuration file path', dest='cfgs_path')
parser.add_argument('-cp', '--compression', default=os.path.join(os.curdir, 'compressions', 'compression_test_final_fp32_64B_pr10'), type=str,
                    help='Compression results file path', dest='comp_path')
parser.add_argument('-al', '--algorithm', default='BDI', type=str,
                    help='Name of target algorithm', dest='target_algo')
parser.add_argument('-md', '--model', default='AlexNet', type=str,
                    help='Name of target model name', dest='target_model')
parser.add_argument('-ld', '--logdirname', default=os.path.join(os.curdir, 'logs'), type=str,
                    help='Directory of output log files', dest='logdirname')
parser.add_argument('-lf', '--logfilename', default='compression_test_result.csv', type=str,
                    help='Name of logfile', dest='logfilename')
args, _ = parser.parse_known_args()


if __name__ == '__main__':
    # 1. Test Configurations

    topo_path = args.topo_path
    cfgs_path = args.cfgs_path
    comp_path = args.comp_path
    target_algo = args.target_algo
    target_model = args.target_model
    logdirname = args.logdirname
    logfilename = args.logfilename
    tmp_dirname = os.path.join(os.curdir, 'temporary', target_model)

    print("On-Chip Buffer Compression Test Configs")
    print(f"- topology path: {topo_path}")
    print(f"- config file path: {cfgs_path}")
    print(f"- compression file: {comp_path}")
    print(f"- target algorithm: {target_algo}")
    print(f"- target model name: {target_model}")
    print(f"- temporary dirname: {tmp_dirname}")
    print(f"- logfilepath: {os.path.join(logdirname, logfilename)}\n")


    # 2. Extract layers and compression ratio of each layer from given files

    tmp_layer_filepath = {}   # save each layer of the given topology file to the 'temporary' directory
    tmp_config_filepath = {}  # generate configurations for each layer by using extracted compression ratio

    with open(topo_path, 'rt') as topo_file:
        content = topo_file.readlines()
        header = content[0]
        body = content[1:]

        os.makedirs(os.path.join(tmp_dirname, 'layers'), exist_ok=True)

        for line in body:
            layer_name = line.split(',')[0].strip()
            tmpfilepath = os.path.join(tmp_dirname, 'layers', layer_name + '.csv')
            tmp_layer_filepath[layer_name] = tmpfilepath

            with open(tmpfilepath, 'wt') as layer_file:
                layer_file.write('\n'.join([header, line]))

        print(f"generated temporary layer files at {tmp_dirname}")

    with open(comp_path, 'rt') as comp_file:
        content = comp_file.readlines()
        header = content[0].split(',')
        body = list(map(lambda x: x.split(','), content[1:]))
        aidx = header.index('Comp Ratio(' + target_algo + ')')

        assert aidx == -1

        os.makedirs(os.path.join(tmp_dirname, 'configs'), exist_ok=True)

        for line in filter(lambda x: target_model in x[0], body):
            layer_type, layer_idx, _ = line[1].split('_')

            if f"{layer_type}_{layer_idx}" not in tmp_config_filepath.keys():
                tmpfilepath = os.path.join(tmp_dirname, 'configs', layer_name + '.cfg')
                tmp_config_filepath[layer_name] = tmpfilepath

                ratio = float(line[aidx])

                config = configparser.ConfigParser()
                config.read(cfgs_path)

                ifmap_sramsiz  = int(config['architecture_presets']['IfmapSramSzkB'])
                filter_sramsiz = int(config['architecture_presets']['FilterSramSzkB'])
                ofmap_sramsiz  = int(config['architecture_presets']['OfmapSramSzkB'])
                bandwidth      = int(config['architecture_presets']['Bandwidth'])

                config['general']['run_name'] = '_'.join([config['general']['run_name'], f"cp_{ratio:.2f}"])
                config['architecture_presets']['IfmapSramSzkB']  = str(math.floor(ifmap_sramsiz * ratio))
                config['architecture_presets']['FilterSramSzkB'] = str(math.floor(filter_sramsiz * ratio))
                config['architecture_presets']['OfmapSramSzkB']  = str(math.floor(ofmap_sramsiz * ratio))
                config['architecture_presets']['Bandwidth']      = str(math.floor(bandwidth * ratio))
                config['run_presets']['InterfaceBandwidth']      = 'USER'

                with open(tmpfilepath, 'wt') as conf_file:
                    config.write(conf_file)

        print("compression ratio extracted")


    # 3. Test using compression ratios and layer configurations

    # parser = argparse.ArgumentParser()
    # parser.add_argument('-t', metavar='Topology file', type=str,
    #                     default=os.path.join(os.curdir, 'topologies', 'conv_nets', 'alexnet.csv'),
    #                     help="Path to the topology file"
    #                     )
    # parser.add_argument('-c', metavar='Config file', type=str,
    #                     default=os.path.join(os.curdir, 'configs', 'google.cfg'),
    #                     help="Path to the config file"
    #                     )
    # parser.add_argument('-p', metavar='log dir', type=str,
    #                     default='auto',
    #                     help="Path to log dir"
    #                     )
    #
    # args = parser.parse_args()
    # topology = args.t
    # temppath = args.c
    # logpath = args.p
    # if logpath == 'auto':
    #     logpath = os.path.join(os.curdir, 'test_runs',
    #                            f'compression_test_'
    #                            f'{temppath.split(os.sep)[-1].split(".")[0]}_'
    #                            f'{topology.split(os.sep)[-1].split(".")[0]}')
    #
    # os.makedirs(logpath, exist_ok=True)
    #
    # buffsize = 256
    #
    # config = configparser.ConfigParser()
    # config.read(temppath)
    # config['general']['run_name'] = '_'.join([config['general']['run_name'], f"bf_{buffsize}"])
    # config['architecture_presets']['IfmapSramSzkB'] = str(buffsize)
    # config['architecture_presets']['FilterSramSzkB'] = str(buffsize)
    # config['architecture_presets']['OfmapSramSzkB'] = str(buffsize)
    # config['run_presets']['InterfaceBandwidth'] = 'USER'



    # buffsizes = [16, 32, 64, 256]
    #
    # for bf in sorted(buffsizes, reverse=True):
    #     config = configparser.ConfigParser()
    #     config.read(temppath)
    #     config['general']['run_name'] = '_'.join([config['general']['run_name'], f"bf_{bf}"])
    #     config['architecture_presets']['IfmapSramSzkB'] = str(bf)
    #     config['architecture_presets']['FilterSramSzkB'] = str(bf)
    #     config['architecture_presets']['OfmapSramSzkB'] = str(bf)
    #     config['run_presets']['InterfaceBandwidth'] = 'USER'
    #
    #     config_filepath = os.path.join(os.curdir, 'configs', '.'.join([config['general']['run_name'], 'cfg']))
    #     with open(config_filepath, 'wt') as file:
    #         config.write(file)
    #
    #     s = scalesim(save_disk_space=True, verbose=True,
    #              config=config_filepath,
    #              topology=topology,
    #              )
    #     s.run_scale(top_path=logpath)
