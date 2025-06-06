'''
Module containing class that provides ROOT dataframe after a given selection
'''
# pylint: disable = import-error
# pylint: disable = too-many-instance-attributes
# pylint: disable = line-too-long
# pylint: disable = invalid-name
# pylint: disable = too-many-arguments, too-many-positional-arguments
# pylint: disable = no-name-in-module

import os
import re
import pprint

import yaml
from dmu.rdataframe.atr_mgr import AtrMgr
from dmu.logging.log_store  import LogStore
from ROOT                   import RDataFrame, TFile

from rx_selection            import cutflow     as cfl
from rx_selection.efficiency import efficiency
from rx_selection.efficiency import ZeroYields

from rx_selection import selection as sel
from rx_selection import utilities as ut

log=LogStore.add_logger('rx_selection:ds_getter')
# -----------------------------------------
class DsGetter:
    '''
    Class used to provide dataframe after a given selection
    '''
    # ------------------------------------
    def __init__(self, cfg : dict):
        self._cfg             = cfg
        ipart                 = cfg['ipart'   ]
        npart                 = cfg['npart'   ]
        self._part            = [ipart, npart ]
        self._q2bin           = cfg['q2bin'   ]
        self._sample          = cfg['sample'  ]
        self._project         = cfg['project' ]
        self._d_redefine_cuts = cfg['redefine']
        self._hlt2            = cfg['hlt2'    ]
        self._cutver          = cfg['cutver'  ]
        self._ipath           = cfg['ipath'   ]

        self._is_sim        : bool
        self._d_sample      : dict

        self._initialized   = False
    # ------------------------------------
    def _initialize(self):
        if self._initialized:
            return

        self._is_sim    = not self._sample.startswith('DATA_')

        self._set_logs()
        self._load_samples()

        self._initialized = True
    # ------------------------------------
    def _load_samples(self) -> None:
        with open(self._ipath, encoding='utf-8') as ifile:
            d_sample = yaml.safe_load(ifile)

        self._d_sample = d_sample
    # ------------------------------------
    def _set_logs(self):
        '''
        Silence log messages of tools
        '''

        LogStore.set_level('dmu:rdataframe:atr_mgr' , 30)
        LogStore.set_level('rx_selection:cutflow'   , 30)
        LogStore.set_level('rx_selection:efficiency', 30)
    # ------------------------------------
    def _update_bdt_cut(self, cut : str, skip_cmb : bool, skip_prec : bool) -> str:
        '''
        Will pick BDT cut, cmb and prec. Will return only one of them, depending on which one is skipped
        If none is skipped, will return original cut
        '''
        if not skip_cmb and not skip_prec:
            log.debug('No bdt cut is skipped, will not redefine')
            return cut

        if cut == '(1)':
            log.debug('No cut was passed, will not redefine')
            return cut

        regex=r'(BDT_cmb\s>\s[0-9\.]+)\s&&\s(BDT_prc\s>\s[0-9\.]+)'
        mtch =re.match(regex, cut)
        if not mtch:
            raise ValueError(f'Cannot match {cut} with {regex}')

        [bdt_cmb, bdt_prc] = mtch.groups()

        return bdt_cmb if skip_prec else bdt_prc
    # ------------------------------------
    def _range_rdf(self, rdf : RDataFrame) -> RDataFrame:
        if self._part is None:
            return rdf

        islice, nslice = self._part

        rdf = ut.get_rdf_range(rdf, islice, nslice)

        return rdf
    # ------------------------------------
    def _get_files_path(self) -> list[str]:
        l_path   = self._d_sample[self._sample][self._hlt2]
        npath    = len(l_path)
        if npath == 0:
            raise FileNotFoundError(f'No files found for: {self._sample}/{self._hlt2}')

        log.info(f'Found {npath} files')

        return l_path
    # ------------------------------------
    def _tree_found(self, l_path : list[str], tree_name : str) -> bool:
        if len(l_path) == 0:
            raise FileNotFoundError('No files found')

        ifile = TFile.Open(l_path[0])

        return hasattr(ifile, tree_name)
    # ------------------------------------
    def _def_from_sel_conf(self) -> dict[str,str]:
        sel_cfg = sel.load_selection_config()
        ana     = self._get_analysis()
        prj     = self._project

        if 'Definitions' not in sel_cfg:
            log.debug('No variable definitions found')
            return {}

        if prj not in sel_cfg['Definitions']:
            log.debug(f'No variable definitions found for project: {prj}')
            return {}

        if ana not in sel_cfg['Definitions'][prj]:
            log.debug(f'No variable definitions found for project/analysis: {prj}/{ana}')
            return {}

        return sel_cfg['Definitions'][prj][ana]
    # ------------------------------------
    def _add_columns(self, rdf : RDataFrame, tree_name : str) -> RDataFrame:
        if tree_name != 'DecayTree':
            log.debug(f'Not adding columns to tree {tree_name}')
            return rdf

        log.info('Adding columns')

        d_def=self._def_from_sel_conf()
        if 'Definitions' in self._cfg:
            log.info('Found definitions in config files')
            d_def.update(self._cfg['Definitions'])

        if len(d_def) == 0:
            log.warning('No definitions found')
            return rdf

        log.info('Defining variables:')

        l_col_name_old = self._get_column_name(rdf)
        for var_name, var_def in d_def.items():
            log.debug(f'    {var_name:<20}{var_def:<60}')
            if var_name in l_col_name_old:
                log.warning(f'Already found variable, cannot define: {var_name} = {var_def}')
                continue

            rdf = rdf.Define(var_name, var_def)

        l_col_name_new = self._get_column_name(rdf)

        nold = len(l_col_name_old)
        nnew = len(l_col_name_new)

        log.info(f'Added columns: {nold} -> {nnew}')

        return rdf
    # ------------------------------------
    def _get_column_name(self, rdf : RDataFrame) -> list[str]:
        v_name = rdf.GetColumnNames()
        l_name = [ name.c_str() for name in v_name ]

        return l_name
    # ------------------------------------
    def _filter_files(self, l_file_path) -> list[str]:
        '''
        This will be needed when running tests
        '''
        if 'max_files' not in self._cfg:
            return l_file_path

        nmax = self._cfg['max_files']

        log.warning(f'Running over at most {nmax} files')

        return l_file_path[:nmax]
    # ------------------------------------
    def _get_rdf_raw(self, tree_name = 'DecayTree') -> RDataFrame:
        log.info(f'Getting dataframe for tree: {tree_name}')
        l_file_path = self._get_files_path()

        if tree_name == 'MCDecayTree' and not self._tree_found(l_file_path, 'MCDecayTree'):
            return None

        nfiles = len(l_file_path)
        log.info(f'Found {nfiles} files with tree {tree_name}')
        for file_path in l_file_path[:10]:
            log.debug(f'   {file_path}')

        l_file_path = self._filter_files(l_file_path)

        rdf = self._rdf_from_path(tree_name, l_file_path)
        rdf = self._range_rdf(rdf)
        rdf = self._add_columns(rdf=rdf, tree_name=tree_name)
        rdf.filepath = l_file_path
        rdf.treename = tree_name

        return rdf
    # ------------------------------------
    def _rdf_from_path(self, tree_name : str, l_file_path : list[str]) -> RDataFrame:
        log.info('Creating dataframe')
        log.debug(f'Tree name: {tree_name}')
        log.debug(f'File path: {l_file_path}')

        if len(l_file_path) == 0:
            raise ValueError('Empty file list')

        d_name = {}
        l_name = []
        for file_path in l_file_path:
            rdf = RDataFrame(tree_name, file_path)
            v_col = rdf.GetColumnNames()
            d_name[file_path] = v_col
            l_name.append(v_col)

        all_equal = all( v_name == l_name[0] for v_name in l_name )
        if all_equal:
            return RDataFrame(tree_name, l_file_path)

        log.error('Found files with different numbers of branches:')
        for path, v_name in d_name.items():
            name = os.path.basename(path)
            size = v_name.size()
            log.info(f'{size:<20}{name:<100}')

        raise ValueError('Invalid input')
    # ------------------------------------
    def _get_gen_nev(self) -> int:
        log.warning('Reading number of entries from MCDecayTree not implemented')

        rdf = self._get_rdf_raw(tree_name = 'MCDecayTree')
        if rdf is None:
            log.warning('MCDecayTree not found, assigning 1 entry to tree')
            return 1

        nev = rdf.Count().GetValue()

        return nev
    # ------------------------------------
    def _redefine_cuts(self, d_cut : dict[str,str]) -> dict[str,str]:
        '''
        Takes dictionary with selection and overrides with with entries in self._d_redefine_cuts
        Returns redefined dictionary
        '''
        for cut_name, new_cut in self._d_redefine_cuts.items():
            if cut_name not in d_cut:
                pprint.pprint(d_cut)
                raise ValueError(f'Cannot redefine {cut_name}, not a valid cut, choose from: {d_cut.keys()}')

            old_cut         = d_cut[cut_name]
            d_cut[cut_name] = new_cut

            old_cut    = re.sub(' +', ' ', old_cut)
            new_cut    = re.sub(' +', ' ', new_cut)

            log.info(f'{cut_name:<15}{old_cut:<70}{"--->":10}{new_cut:<40}')

        return d_cut
    # ------------------------------------
    def _add_reco_efficiency(self, cf : cfl.cutflow, nrec : int, truth_string : str) -> cfl.cutflow:
        '''
        Takes cutflow and nreco to calculate the reco efficiency and add it to the cutflow
        Returns updated cutflow
        '''
        if not self._is_sim:
            return cf

        ngen = self._get_gen_nev()

        cf['reco'] = efficiency(nrec, ngen - nrec, cut=truth_string)

        return cf
    # ------------------------------------
    def _get_analysis(self):
        hlt2_nomva = self._hlt2.replace('_MVA', '')

        if hlt2_nomva.endswith('EE'):
            return 'EE'

        if hlt2_nomva.endswith('MuMu'):
            return 'MM'

        raise ValueError(f'Usupported HLT2 trigger: {hlt2_nomva}')
    # ----------------------------------------
    def _redefine_cut(self, cut_name : str, cut_value : str) -> str:
        '''
        Takes cut, checks if it is meant to be redefined, returns updated value
        '''
        if cut_name not in self._d_redefine_cuts:
            return cut_value

        new_cut = self._d_redefine_cuts[cut_name]
        cut     = new_cut

        log.warning(f'{cut_name:<20}{"->":<20}{cut:<100}')

        return cut
    # ----------------------------------------
    def get_rdf(self) -> RDataFrame:
        '''
        Returns ROOT dataframe after selection
        '''

        self._initialize()

        rdf   = self._get_rdf_raw()
        dfmgr = AtrMgr(rdf)
        d_cut = sel.selection(
                analysis = self._get_analysis(),
                project  = self._project,
                q2bin    = self._q2bin,
                process  = self._sample)
        rdf   = dfmgr.add_atr(rdf)
        cf    = cfl.cutflow(d_meta = {'file' : rdf.filepath, 'tree' : rdf.treename})
        tot   = rdf.Count().GetValue()
        d_cut = self._redefine_cuts(d_cut)

        log.info(f'Applying selection version: {self._cutver}')

        for cut_name, cut in d_cut.items():
            log.info(f'{"":<10}{cut_name:>20}')

            cut = self._redefine_cut(cut_name, cut)
            rdf = rdf.Filter(cut, cut_name)
            pas = rdf.Count().GetValue()

            log.debug(f'{cut_name:<20}{"--->":20}{cut:<100}')

            if cut_name == 'truth' and self._is_sim:
                cf = self._add_reco_efficiency(cf, pas, cut)
                tot= pas
                continue

            try:
                eff = efficiency(pas, tot - pas, cut=cut)
            except ZeroYields:
                log.error(f'Last cut ({cut}) passed zero events:')
                print(cf)
                raise

            cf[cut_name] = eff

            tot=pas

        rdf          = dfmgr.add_atr(rdf)
        rdf.treename = 'DecayTree'
        rdf.cf       = cf

        return rdf
# -----------------------------------------
