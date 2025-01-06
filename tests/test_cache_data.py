'''
Module with tests for CacheData class
'''
import os
import glob
from typing        import Union
from dataclasses   import dataclass

import pytest
from dmu.logging.log_store   import LogStore
from rx_selection.cache_data import CacheData

log = LogStore.add_logger('rx_selection:test_cache_data')
# ---------------------------------------------
@dataclass
class Data:
    '''
    Class used to share data
    '''
    l_sam_trg : list[tuple[str,str]]
    data_version = 'v1'
    d_rk_trigger = {
            'ee' : 'Hlt2RD_BuToKpEE_MVA',
            'mm' : 'Hlt2RD_BuToKpMuMu_MVA',
            }
# ---------------------------------------------
def _trigger_from_sample(sample_name : str, is_rk : bool) -> Union[None,str]:
    if sample_name.startswith('DATA_'):
        return None

    d_trigger = Data.d_rk_trigger if is_rk else Data.d_rkst_trigger

    if  'ee'  in sample_name:
        return d_trigger['ee']

    if  'eplemn'  in sample_name:
        return d_trigger['ee']

    if '_mm_' in sample_name:
        return d_trigger['mm']

    if 'mumu' in sample_name:
        return d_trigger['mm']

    log.warning(f'Cannot determine trigger, skipping {sample_name}')

    return None
# ---------------------------------------------
def _get_samples(is_rk : bool) -> list[tuple[str,str]]:
    if hasattr(Data, 'l_sam_trg'):
        return Data.l_sam_trg

    if 'DATADIR' not in os.environ:
        raise ValueError('DATADIR not found in environment')

    data_dir   = os.environ['DATADIR']
    sample_dir = f'{data_dir}/RX_run3/{Data.data_version}/post_ap'
    l_sam_trg  = []
    for sample_path in glob.glob(f'{sample_dir}/*'):
        sample_name = os.path.basename(sample_path)
        trigger     = _trigger_from_sample(sample_name, is_rk)
        if trigger is None:
            continue

        l_sam_trg.append((sample_name, trigger))

    nsample = len(l_sam_trg)
    log.info(f'Found {nsample} samples')

    l_sam_trg = l_sam_trg[:2]

    Data.l_sam_trg = l_sam_trg

    return l_sam_trg
# ---------------------------------------------
def _get_config(sample : str, trigger : str, is_rk : bool) -> dict:
    '''
    Takes name to config file
    Return settings from YAML as dictionary
    '''
    d_conf            = {}
    d_conf['ipart'  ] = 0
    d_conf['npart'  ] = 1000
    d_conf['ipath'  ] = '/publicfs/ucas/user/campoverde/Data/RX_run3/v1/post_ap'
    d_conf['sample' ] = sample
    d_conf['project'] = 'RK' if is_rk else 'RKst'
    d_conf['q2bin'  ] = 'central'
    d_conf['hlt2'   ] = trigger
    d_conf['cutver' ] = 'v1'
    d_conf['remove' ] = ['q2', 'bdt']

    return d_conf
# ---------------------------------------------
@pytest.mark.parametrize('sample, trigger', _get_samples(is_rk=True))
def test_run3_rk(sample : str, trigger : str):
    '''
    Testing on run3 RK samples and triggers
    '''
    log.info(f'{sample:<60}{trigger:<40}')
    cfg = _get_config(sample, trigger, is_rk = True)

    obj=CacheData(cfg = cfg)
    obj.save()
