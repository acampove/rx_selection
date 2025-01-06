'''
Module containing functions used for truth matching
'''
# pylint: disable=line-too-long, import-error, too-many-statements, invalid-name, too-many-branches

from typing import Union

from dmu.logging.log_store  import LogStore


log=LogStore.add_logger('rx_selection:truth_matching')

# ----------------------------------------------------------
def _get_inclusive_match(lep : int, mes : int) -> str:
    '''
    Function taking the lepton ID (11, 13, etc) and the meson ID (511, 521, etc)
    and returning truth matching string for inclusive decays
    '''
    ll        = f'((TMath::Abs(L1_TRUEID)=={lep}) && (TMath::Abs(L2_TRUEID)=={lep}))'
    ll_mother =  '(((TMath::Abs(Jpsi_TRUEID)==443) && (TMath::Abs(L1_MC_MOTHER_ID)==443) && (TMath::Abs(L2_MC_MOTHER_ID)==443)) || ((TMath::Abs(Jpsi_TRUEID)==100443) && (TMath::Abs(L1_MC_MOTHER_ID)==100443) && (TMath::Abs(L2_MC_MOTHER_ID)==100443)))'
    Bx        = f'TMath::Abs(B_TRUEID)=={mes}'

    return f'({ll}) && ({ll_mother}) && ({Bx})'
# ----------------------------------------------------------
def _get_no_reso(channel : str) -> str:
    '''
    Will return truth matching string needed to remove Jpsi, psi2S and cabibbo suppressed components
    Needed when using inclusive samples
    '''
    if channel == 'ee':
        ctrl_ee    = get_truth('12153001')
        psi2_ee    = get_truth('12153012')
        ctrl_pi_ee = get_truth('12153020')

        return f'!({ctrl_ee}) && !({psi2_ee}) && !({ctrl_pi_ee})'

    if channel == 'mm':
        ctrl_mm    = get_truth('12143001')
        psi2_mm    = get_truth('12143020')
        ctrl_pi_mm = get_truth('12143010')

        return f'!({ctrl_mm}) && !({psi2_mm}) && !({ctrl_pi_mm})'

    raise ValueError(f'Invalid channel: {channel}')
# ----------------------------------------------------------
def get_truth(event_type : Union[int,str]) -> str:
    '''
    Function meant to return truth matching string from event type string
    For data it will return '(1)'
    '''
    if isinstance(event_type, int):
        event_type=str(event_type)

    log.info(f'Applying truth matching to event_type: {event_type}')

    if     event_type.startswith('DATA_'):
        cut = '(1)'
    elif   event_type in ['12113001', '12113002']:
        #rare mumu
        cut= 'TMath::Abs(B_TRUEID) == 521 && TMath::Abs(L1_TRUEID) == 13 && TMath::Abs(L2_TRUEID) == 13 && TMath::Abs(L1_MC_MOTHER_ID) == 521 && TMath::Abs(L2_MC_MOTHER_ID) == 521 && TMath::Abs(H_TRUEID) == 321 && TMath::Abs(H_MC_MOTHER_ID) == 521'
    elif   event_type in ['12113024']:
        # B+ pi mumu
        cut= 'TMath::Abs(B_TRUEID) == 521  && TMath::Abs(L1_TRUEID) == 13 && TMath::Abs(L2_TRUEID) == 13 && TMath::Abs(L1_MC_MOTHER_ID) == 521  && TMath::Abs(L2_MC_MOTHER_ID) == 521  && TMath::Abs(H_TRUEID) == 211 && TMath::Abs(H_MC_MOTHER_ID) == 521'
    elif   event_type == '15114021':
        # Lb pi pi mumu
        cut= 'TMath::Abs(B_TRUEID) == 5122 && TMath::Abs(L1_TRUEID) == 13 && TMath::Abs(L2_TRUEID) == 13 && TMath::Abs(L1_MC_MOTHER_ID) == 5122 && TMath::Abs(L2_MC_MOTHER_ID) == 5122 && TMath::Abs(H_TRUEID) == 211 && TMath::Abs(H_MC_MOTHER_ID) == 5122'
    elif event_type in ['12123001', '12123002', '12123003', '12123005']:
        # B+ -> K+ee
        cut= 'TMath::Abs(B_TRUEID) == 521 && TMath::Abs(L1_TRUEID) == 11 && TMath::Abs(L2_TRUEID) == 11 && TMath::Abs(L1_MC_MOTHER_ID) == 521 && TMath::Abs(L2_MC_MOTHER_ID) == 521 && TMath::Abs(H_TRUEID) == 321 && TMath::Abs(H_MC_MOTHER_ID) == 521'
    elif event_type in ['12143001']:
        #reso Jpsi mumu
        cut= 'TMath::Abs(B_TRUEID) == 521 && TMath::Abs(Jpsi_TRUEID) == 443 && TMath::Abs(Jpsi_MC_MOTHER_ID) == 521 && TMath::Abs(L1_TRUEID) == 13 && TMath::Abs(L2_TRUEID) == 13 && TMath::Abs(L1_MC_MOTHER_ID) == 443 && TMath::Abs(L2_MC_MOTHER_ID) == 443 && TMath::Abs(H_TRUEID) == 321 && TMath::Abs(H_MC_MOTHER_ID) == 521'#reso Jpsi mumu
    elif event_type in ['12153001']:
        #reso Jpsi ee
        cut= 'TMath::Abs(B_TRUEID) == 521 && TMath::Abs(Jpsi_TRUEID) == 443 && TMath::Abs(Jpsi_MC_MOTHER_ID) == 521 && TMath::Abs(L1_TRUEID) == 11 && TMath::Abs(L2_TRUEID) == 11 && TMath::Abs(L1_MC_MOTHER_ID) == 443 && TMath::Abs(L2_MC_MOTHER_ID) == 443 && TMath::Abs(H_TRUEID) == 321 && TMath::Abs(H_MC_MOTHER_ID) == 521'#reso Jpsi ee
    elif event_type in ['12143020']:
        #reso Psi mumu
        cut= 'TMath::Abs(B_TRUEID) == 521 && TMath::Abs(Jpsi_TRUEID) == 100443 && TMath::Abs(Jpsi_MC_MOTHER_ID) == 521 && TMath::Abs(L1_TRUEID) == 13 && TMath::Abs(L2_TRUEID) == 13 && TMath::Abs(L1_MC_MOTHER_ID) == 100443 && TMath::Abs(L2_MC_MOTHER_ID) == 100443 && TMath::Abs(H_TRUEID) == 321 && TMath::Abs(H_MC_MOTHER_ID) == 521'#reso Psi mumu
    elif event_type in ['12153012']:
        #reso Psi ee
        cut= 'TMath::Abs(B_TRUEID) == 521 && TMath::Abs(Jpsi_TRUEID) == 100443 && TMath::Abs(Jpsi_MC_MOTHER_ID) == 521 && TMath::Abs(L1_TRUEID) == 11 && TMath::Abs(L2_TRUEID) == 11 && TMath::Abs(L1_MC_MOTHER_ID) == 100443 && TMath::Abs(L2_MC_MOTHER_ID) == 100443 && TMath::Abs(H_TRUEID) == 321 && TMath::Abs(H_MC_MOTHER_ID) == 521'#reso Psi ee
    elif event_type in ['12143010']:
        #reso jpsi pi mumu
        cut= 'TMath::Abs(B_TRUEID) == 521 && TMath::Abs(Jpsi_TRUEID) == 443 && TMath::Abs(Jpsi_MC_MOTHER_ID) == 521 && TMath::Abs(L1_TRUEID) == 13 && TMath::Abs(L2_TRUEID) == 13 && TMath::Abs(L1_MC_MOTHER_ID) == 443 && TMath::Abs(L2_MC_MOTHER_ID) == 443 && TMath::Abs(H_TRUEID) == 211 && TMath::Abs(H_MC_MOTHER_ID) == 521'#reso jpsi pi mumu
    elif event_type in ['12153020']:
        #reso jpsi pi ee
        cut= 'TMath::Abs(B_TRUEID) == 521 && TMath::Abs(Jpsi_TRUEID) == 443 && TMath::Abs(Jpsi_MC_MOTHER_ID) == 521 && TMath::Abs(L1_TRUEID) == 11 && TMath::Abs(L2_TRUEID) == 11 && TMath::Abs(L1_MC_MOTHER_ID) == 443 && TMath::Abs(L2_MC_MOTHER_ID) == 443 && TMath::Abs(H_TRUEID) == 211 && TMath::Abs(H_MC_MOTHER_ID) == 521'#reso jpsi pi ee
    elif event_type in ['12125101']:
        #reso B+ -> (K*+ -> (K_S0 -> pi+ pi-) pi+) e+ e-
        cut= 'TMath::Abs(B_TRUEID) == 521 && TMath::Abs(L1_TRUEID) == 11 && TMath::Abs(L2_TRUEID) == 11 && TMath::Abs(L1_MC_MOTHER_ID) == 521 && TMath::Abs(L2_MC_MOTHER_ID) == 521 && TMath::Abs(H_TRUEID) == 211 && (TMath::Abs(H_MC_MOTHER_ID) == 310 || TMath::Abs(H_MC_MOTHER_ID) == 323)'
    #-------------------------------------------------------------
    elif event_type == '11453001':
        #Bd->XcHs
        pick     = _get_inclusive_match(lep=11, mes=511)
        no_reso  = _get_no_reso(channel = 'ee')

        cut      = f'({pick}) && ({no_reso})'
    elif event_type == '12952000':
        #B+->XcHs
        pick     = _get_inclusive_match(lep=11, mes=521)
        no_reso  = _get_no_reso(channel = 'ee')

        cut      = f'({pick}) && ({no_reso})'
    elif event_type == '13454001':
        #Bs->XcHs
        pick     = _get_inclusive_match(lep=11, mes=531)
        no_reso  = _get_no_reso(channel = 'ee')

        cut      = f'({pick}) && ({no_reso})'
    #-------------------------------------------------------------
    elif event_type == '11442001':
        # bdXcHs_mm
        pick     = _get_inclusive_match(lep=13, mes=511)
        no_reso  = _get_no_reso(channel = 'mm')

        cut      = f'({pick}) && ({no_reso})'
    elif event_type == '12442001':
        # bpXcHs_mm
        pick     = _get_inclusive_match(lep=13, mes=521)
        no_reso  = _get_no_reso(channel = 'mm')

        cut      = f'({pick}) && ({no_reso})'
    elif event_type == '13442001':
        # bsXcHs_mm
        pick     = _get_inclusive_match(lep=13, mes=531)
        no_reso  = _get_no_reso(channel = 'mm')

        cut      = f'({pick}) && ({no_reso})'
    elif event_type == '15442001':
        # LbXcHs_mm
        pick     = _get_inclusive_match(lep=13, mes=5122)
        no_reso  = _get_no_reso(channel = 'mm')

        cut      = f'({pick}) && ({no_reso})'
    #-------------------------------------------------------------
    elif event_type == '12155100':
        #exclusive jpsi kst ee Bu
        cut= 'TMath::Abs(B_TRUEID) == 521 && TMath::Abs(Jpsi_TRUEID) == 443 && TMath::Abs(Jpsi_MC_MOTHER_ID) == 521 && TMath::Abs(L1_TRUEID) == 11 && TMath::Abs(L2_TRUEID) == 11 && TMath::Abs(L1_MC_MOTHER_ID) == 443 && TMath::Abs(L2_MC_MOTHER_ID) == 443 && TMath::Abs(H_TRUEID) == 211 && (TMath::Abs(H_MC_MOTHER_ID) == 323 or TMath::Abs(H_MC_MOTHER_ID) == 310) && (TMath::Abs(H_MC_GD_MOTHER_ID) == 521 or TMath::Abs(H_MC_GD_MOTHER_ID) == 323)'#exclusive Jpsi kst ee
    elif event_type == '11154100':
        #  B0 -> (KS0 -> pi+ pi-) (J/psi(1S) -> e+ e-)
        cut= 'TMath::Abs(B_TRUEID) == 511 && TMath::Abs(Jpsi_TRUEID) == 443 && TMath::Abs(Jpsi_MC_MOTHER_ID) == 511 && TMath::Abs(L1_TRUEID) == 11 && TMath::Abs(L2_TRUEID) == 11 && TMath::Abs(L1_MC_MOTHER_ID) == 443 && TMath::Abs(L2_MC_MOTHER_ID) == 443 && TMath::Abs(H_TRUEID) == 211 && TMath::Abs(H_MC_MOTHER_ID) == 310'
    elif event_type == '11154001':
        #exclusive jpsi kst ee Bd
        cut= 'TMath::Abs(B_TRUEID) == 511 && TMath::Abs(Jpsi_TRUEID) == 443 && TMath::Abs(Jpsi_MC_MOTHER_ID) == 511 && TMath::Abs(L1_TRUEID) == 11 && TMath::Abs(L2_TRUEID) == 11 && TMath::Abs(L1_MC_MOTHER_ID) == 443 && TMath::Abs(L2_MC_MOTHER_ID) == 443 && TMath::Abs(H_TRUEID) == 321 && TMath::Abs(H_MC_MOTHER_ID) == 313'#exclusive Jpsi kst ee Bd
    elif event_type == '13454001':
        #reso jpsi kst ee Bs
        cut= 'TMath::Abs(B_TRUEID) == 531 && TMath::Abs(Jpsi_TRUEID) == 443 && TMath::Abs(Jpsi_MC_MOTHER_ID) == 531 && TMath::Abs(L1_TRUEID) == 11 && TMath::Abs(L2_TRUEID) == 11 && TMath::Abs(L1_MC_MOTHER_ID) == 443 && TMath::Abs(L2_MC_MOTHER_ID) == 443 && TMath::Abs(H_TRUEID) == 321 && TMath::Abs(H_MC_MOTHER_ID) == 313'#reso Jpsi kst ee
    elif event_type in ['13144010', '13144011']:
        # Bs Jpsi(mm) Phi(kk)
        cut= 'TMath::Abs(B_TRUEID) == 531 && TMath::Abs(Jpsi_TRUEID) == 443 && TMath::Abs(Jpsi_MC_MOTHER_ID) == 531 && TMath::Abs(L1_TRUEID) == 13 && TMath::Abs(L2_TRUEID) == 13 && TMath::Abs(L1_MC_MOTHER_ID) == 443 && TMath::Abs(L2_MC_MOTHER_ID) == 443 && TMath::Abs(H_TRUEID) == 321 && TMath::Abs(H_MC_MOTHER_ID) == 333'#reso Jpsi kst ee
    elif event_type in ['13154001']:
        # Bs Jpsi(ee) Phi(kk)
        cut= 'TMath::Abs(B_TRUEID) == 531 && TMath::Abs(Jpsi_TRUEID) == 443 && TMath::Abs(Jpsi_MC_MOTHER_ID) == 531 && TMath::Abs(L1_TRUEID) == 11 && TMath::Abs(L2_TRUEID) == 11 && TMath::Abs(L1_MC_MOTHER_ID) == 443 && TMath::Abs(L2_MC_MOTHER_ID) == 443 && TMath::Abs(H_TRUEID) == 321 && TMath::Abs(H_MC_MOTHER_ID) == 333'#reso Jpsi kst ee
    elif event_type in ['11154011']:
        #Bd->psi2S(=>ee) K*
        cut= 'TMath::Abs(B_TRUEID) == 511 && TMath::Abs(Jpsi_TRUEID) == 100443 && TMath::Abs(Jpsi_MC_MOTHER_ID) == 511 && TMath::Abs(L1_TRUEID) == 11 && TMath::Abs(L2_TRUEID) == 11 && TMath::Abs(L1_MC_MOTHER_ID) == 100443 && TMath::Abs(L2_MC_MOTHER_ID) == 100443 && TMath::Abs(H_TRUEID) == 321 && TMath::Abs(H_MC_MOTHER_ID) == 313'#reso Psi kst ee
    elif event_type == '11453012':
        #reso Psi X
        cut= 'TMath::Abs(B_TRUEID) == 511 && TMath::Abs(Jpsi_TRUEID) == 100443 && TMath::Abs(Jpsi_MC_MOTHER_ID) == 511 && TMath::Abs(L1_TRUEID) == 11 && TMath::Abs(L2_TRUEID) == 11 && TMath::Abs(L1_MC_MOTHER_ID) == 100443 && TMath::Abs(L2_MC_MOTHER_ID) == 100443'#reso Psi(ee) X
    elif event_type == '11124002':
        #Bd K*(k pi) ee.
        cut= 'TMath::Abs(B_TRUEID) == 511 && TMath::Abs(L1_TRUEID) == 11 && TMath::Abs(L2_TRUEID) == 11 && TMath::Abs(L1_MC_MOTHER_ID) == 511 && TMath::Abs(L2_MC_MOTHER_ID) == 511 && (TMath::Abs(H_TRUEID) == 321 or TMath::Abs(H_TRUEID) == 211) && TMath::Abs(H_MC_MOTHER_ID) == 313'
    elif event_type == '11114014':
        #Bd K*(k pi) mm
        cut= 'TMath::Abs(B_TRUEID) == 511 && TMath::Abs(L1_TRUEID) == 13 && TMath::Abs(L2_TRUEID) == 13 && TMath::Abs(L1_MC_MOTHER_ID) == 511 && TMath::Abs(L2_MC_MOTHER_ID) == 511 && (TMath::Abs(H_TRUEID) == 321 or TMath::Abs(H_TRUEID) == 211) && TMath::Abs(H_MC_MOTHER_ID) == 313'
    elif event_type == '11124037':
        #Bd (k pi) ee.
        cut= 'TMath::Abs(B_TRUEID) == 511 && TMath::Abs(L1_TRUEID) == 11 && TMath::Abs(L2_TRUEID) == 11 && TMath::Abs(L1_MC_MOTHER_ID) == 511 && TMath::Abs(L2_MC_MOTHER_ID) == 511 && (TMath::Abs(H_TRUEID) == 321 or TMath::Abs(H_TRUEID) == 211) && TMath::Abs(H_MC_MOTHER_ID) == 511'
    elif event_type == '12123445':
        #B+ -> K*+ ee
        cut= 'TMath::Abs(B_TRUEID) == 521 &&  TMath::Abs(L1_TRUEID) ==  11 &&  TMath::Abs(L2_TRUEID) == 11 &&  TMath::Abs(L1_MC_MOTHER_ID)  == 521 &&  TMath::Abs(L2_MC_MOTHER_ID) == 521 &&  TMath::Abs(H_TRUEID) == 321 && TMath::Abs(H_MC_MOTHER_ID) == 323'
    elif event_type == '13124006':
        #Bs -> phi(-> KK) ee
        cut= 'TMath::Abs(B_TRUEID) == 531 &&  TMath::Abs(L1_TRUEID) ==  11 &&  TMath::Abs(L2_TRUEID) == 11 &&  TMath::Abs(L1_MC_MOTHER_ID)  == 531 &&  TMath::Abs(L2_MC_MOTHER_ID) == 531 &&  TMath::Abs(H_TRUEID) == 321 && TMath::Abs(H_MC_MOTHER_ID) == 333'
    elif event_type == '13124401':
        # Bs -> phi(-> KK) eta(-> ee gamma)
        cut= 'TMath::Abs(B_TRUEID) == 531 &&  TMath::Abs(L1_TRUEID) ==  11 &&  TMath::Abs(L2_TRUEID) == 11 &&  TMath::Abs(L1_MC_MOTHER_ID)  == 221 &&  TMath::Abs(L2_MC_MOTHER_ID) == 221 &&  TMath::Abs(H_TRUEID) == 321 && TMath::Abs(H_MC_MOTHER_ID) == 333'
    elif event_type == '11124401':
        # B0 -> (eta -> e+ e- gamma) (K*0 -> K+ pi- )
        cut= 'TMath::Abs(B_TRUEID) == 511 &&  TMath::Abs(L1_TRUEID) ==  11 &&  TMath::Abs(L2_TRUEID) == 11 &&  TMath::Abs(L1_MC_MOTHER_ID)  == 221 &&  TMath::Abs(L2_MC_MOTHER_ID) == 221 && (TMath::Abs(H_TRUEID) == 321 ||  TMath::Abs(H_TRUEID) == 211) && TMath::Abs(H_MC_MOTHER_ID) == 313'
    elif event_type == '13124402':
        #Bs -> phi(-> KK) pi0(-> ee gamma)
        cut= 'TMath::Abs(B_TRUEID) == 531 &&  TMath::Abs(L1_TRUEID) ==  11 &&  TMath::Abs(L2_TRUEID) == 11 &&  TMath::Abs(L1_MC_MOTHER_ID)  == 111 &&  TMath::Abs(L2_MC_MOTHER_ID) == 111 &&  TMath::Abs(H_TRUEID) == 321 && TMath::Abs(H_MC_MOTHER_ID) == 333'
    elif event_type == '12425000':
        #B+ -> K_1(K pipi) ee
        cut= 'TMath::Abs(B_TRUEID) == 521 &&  TMath::Abs(L1_TRUEID) ==  11 &&  TMath::Abs(L2_TRUEID) == 11 &&  TMath::Abs(L1_MC_MOTHER_ID)  == 521 &&  TMath::Abs(L2_MC_MOTHER_ID) == 521 &&  (TMath::Abs(H_TRUEID) == 321 || TMath::Abs(H_TRUEID) == 211) && (TMath::Abs(H_MC_MOTHER_ID) == 10323 || TMath::Abs(H_MC_MOTHER_ID) == 113 || TMath::Abs(H_MC_MOTHER_ID) == 223 || TMath::Abs(H_MC_MOTHER_ID) == 313)'
    elif event_type == '12155020':
        #B+ -> K_1(K pipi) Jpsi(ee)
        cut= 'TMath::Abs(B_TRUEID) == 521 &&  TMath::Abs(L1_TRUEID) ==  11 &&  TMath::Abs(L2_TRUEID) == 11 &&  TMath::Abs(L1_MC_MOTHER_ID)  == 443 &&  TMath::Abs(L2_MC_MOTHER_ID) == 443 &&  (TMath::Abs(H_TRUEID) == 321 || TMath::Abs(H_TRUEID) == 211) && TMath::Abs(H_MC_MOTHER_ID) == 10323'
    elif event_type == '12145090':
        #B+ -> K_1(K pipi) Jpsi(ee)
        cut= 'TMath::Abs(B_TRUEID) == 521 &&  TMath::Abs(L1_TRUEID) ==  13 &&  TMath::Abs(L2_TRUEID) == 13 &&  TMath::Abs(L1_MC_MOTHER_ID)  == 443 &&  TMath::Abs(L2_MC_MOTHER_ID) == 443 &&  (TMath::Abs(H_TRUEID) == 321 || TMath::Abs(H_TRUEID) == 211) && TMath::Abs(H_MC_MOTHER_ID) == 10323'
    elif event_type == '12425011':
        #B+ -> K_2(X -> K pipi) ee
        cut= 'TMath::Abs(B_TRUEID) == 521 &&  TMath::Abs(L1_TRUEID) ==  11 &&  TMath::Abs(L2_TRUEID) == 11 &&  TMath::Abs(L1_MC_MOTHER_ID)  == 521 &&  TMath::Abs(L2_MC_MOTHER_ID) == 521 &&  (TMath::Abs(H_TRUEID) == 321 || TMath::Abs(H_TRUEID) == 211) && (TMath::Abs(H_MC_MOTHER_ID) ==   325 || TMath::Abs(H_MC_MOTHER_ID) == 113 || TMath::Abs(H_MC_MOTHER_ID) == 223 || TMath::Abs(H_MC_MOTHER_ID) == 313)'
    elif event_type == '12155110':
        #B+->K*+ psi2S(-> ee)
        cut= 'TMath::Abs(B_TRUEID) == 521 &&  TMath::Abs(L1_TRUEID) ==  11 &&  TMath::Abs(L2_TRUEID) == 11 && TMath::Abs(L1_MC_MOTHER_ID)  == 100443 && TMath::Abs(L2_MC_MOTHER_ID) == 100443 && TMath::Abs(H_TRUEID) == 211 && (TMath::Abs(H_MC_MOTHER_ID) == 323 or TMath::Abs(H_MC_MOTHER_ID) == 310)'
    elif event_type == '12103025':
        #B+ -> K+ pi pi
        cut= 'TMath::Abs(B_TRUEID)  == 521 &&  TMath::Abs(L1_TRUEID)  == 211 &&  TMath::Abs(L2_TRUEID) == 211 &&  TMath::Abs(L1_MC_MOTHER_ID)  == 521 &&  TMath::Abs(L2_MC_MOTHER_ID) == 521 &&  TMath::Abs(H_TRUEID) == 321 &&  TMath::Abs(H_MC_MOTHER_ID) == 521'
    elif event_type == '12103017':
        #B+ -> K+ K K
        cut= 'TMath::Abs(B_TRUEID)  == 521 &&  TMath::Abs(L1_TRUEID)  == 321 &&  TMath::Abs(L2_TRUEID) == 321 &&  TMath::Abs(L1_MC_MOTHER_ID)  == 521 &&  TMath::Abs(L2_MC_MOTHER_ID) == 521 &&  TMath::Abs(H_TRUEID) == 321 &&  TMath::Abs(H_MC_MOTHER_ID) == 521'
    elif event_type == '12583021':
        #bpd0kpenuenu
        tm_par = 'TMath::Abs(B_TRUEID)  == 521 &&  TMath::Abs(L1_TRUEID)  == 11 &&  TMath::Abs(L2_TRUEID) == 11'
        tm_dt1 = 'TMath::Abs(L1_MC_MOTHER_ID)  == 521 || TMath::Abs(L1_MC_MOTHER_ID) == 421'
        tm_dt2 = 'TMath::Abs(L2_MC_MOTHER_ID)  == 521 || TMath::Abs(L2_MC_MOTHER_ID) == 421'
        cut    = f'({tm_par}) && ({tm_dt1}) && ({tm_dt2}) && TMath::Abs(H_TRUEID) == 321 &&  TMath::Abs(H_MC_MOTHER_ID) == 421'
    elif event_type == '12183004':
        # bpd0kpenupi
        tm_par = 'TMath::Abs(B_TRUEID)  == 521 &&  (TMath::Abs(L1_TRUEID)  == 11 || TMath::Abs(L1_TRUEID)  == 211) &&  (TMath::Abs(L2_TRUEID) == 11 || TMath::Abs(L2_TRUEID) == 211)'
        tm_dt1 = 'TMath::Abs(L1_MC_MOTHER_ID)  == 521 || TMath::Abs(L1_MC_MOTHER_ID) == 421'
        tm_dt2 = 'TMath::Abs(L2_MC_MOTHER_ID)  == 521 || TMath::Abs(L2_MC_MOTHER_ID) == 421'
        cut    = f'({tm_par}) && ({tm_dt1}) && ({tm_dt2}) && TMath::Abs(H_TRUEID) == 321 &&  TMath::Abs(H_MC_MOTHER_ID) == 421'
    elif event_type == '12583013':
        # bpd0kppienu
        tm_par = 'TMath::Abs(B_TRUEID)  == 521 &&  (TMath::Abs(L1_TRUEID)  == 11 || TMath::Abs(L1_TRUEID)  == 211) &&  (TMath::Abs(L2_TRUEID) == 11 || TMath::Abs(L2_TRUEID) == 211)'
        tm_dt1 = 'TMath::Abs(L1_MC_MOTHER_ID)  == 521 || TMath::Abs(L1_MC_MOTHER_ID) == 421'
        tm_dt2 = 'TMath::Abs(L2_MC_MOTHER_ID)  == 521 || TMath::Abs(L2_MC_MOTHER_ID) == 421'
        cut    = f'({tm_par}) && ({tm_dt1}) && ({tm_dt2}) && TMath::Abs(H_TRUEID) == 321 &&  TMath::Abs(H_MC_MOTHER_ID) == 421'
    #------------------------------------------------------------
    elif event_type == '11154011':
        tm_par = 'TMath::Abs(B_TRUEID)        == 511    && TMath::Abs(L1_TRUEID)       == 11     && TMath::Abs(L2_TRUEID)   == 11 && TMath::Abs(H_TRUEID) == 321'
        tm_psi = 'TMath::Abs(L1_MC_MOTHER_ID) == 100443 && TMath::Abs(L2_MC_MOTHER_ID) == 100443 && TMath::Abs(Jpsi_TRUEID) == 100443'
        tm_kst = 'TMath::Abs(H_MC_MOTHER_ID)  == 313'

        cut    = f'{tm_par} && {tm_psi} && {tm_kst}'
    elif event_type == '11144011':
        tm_par = 'TMath::Abs(B_TRUEID)        == 511    && TMath::Abs(L1_TRUEID)       == 13     && TMath::Abs(L2_TRUEID)   == 13 && TMath::Abs(H_TRUEID) == 321'
        tm_psi = 'TMath::Abs(L1_MC_MOTHER_ID) == 100443 && TMath::Abs(L2_MC_MOTHER_ID) == 100443 && TMath::Abs(Jpsi_TRUEID) == 100443'
        tm_kst = 'TMath::Abs(H_MC_MOTHER_ID)  == 313'

        cut    = f'{tm_par} && {tm_psi} && {tm_kst}'
    elif event_type == '11114002':
        # B0-> mu+ mu- (K*(892)0 -> K+ pi-)
        tm_par = 'TMath::Abs(B_TRUEID)        == 511    && TMath::Abs(L1_TRUEID)       == 13     && TMath::Abs(L2_TRUEID)   == 13 && TMath::Abs(H_TRUEID) == 321'
        tm_psi = 'TMath::Abs(L1_MC_MOTHER_ID) == 511    && TMath::Abs(L2_MC_MOTHER_ID) == 511'
        tm_kst = 'TMath::Abs(H_MC_MOTHER_ID)  == 313'

        cut    = f'{tm_par} && {tm_psi} && {tm_kst}'
    #------------------------------------------------------------
    elif event_type == '12155110':
        tm_par = 'TMath::Abs(B_TRUEID)        == 521    && TMath::Abs(L1_TRUEID)       == 11     && TMath::Abs(L2_TRUEID)   == 11 && TMath::Abs(H_TRUEID) == 211'
        tm_psi = 'TMath::Abs(L1_MC_MOTHER_ID) == 100443 && TMath::Abs(L2_MC_MOTHER_ID) == 100443 && TMath::Abs(Jpsi_TRUEID) == 100443'
        tm_kst = 'TMath::Abs(H_MC_MOTHER_ID)  == 323'

        cut    = f'{tm_par} && {tm_psi} && {tm_kst}'
    elif event_type == '12145120':
        tm_par = 'TMath::Abs(B_TRUEID)        == 521    && TMath::Abs(L1_TRUEID)       == 13     && TMath::Abs(L2_TRUEID)   == 13 && TMath::Abs(H_TRUEID) == 211'
        tm_psi = 'TMath::Abs(L1_MC_MOTHER_ID) == 100443 && TMath::Abs(L2_MC_MOTHER_ID) == 100443 && TMath::Abs(Jpsi_TRUEID) == 100443'
        tm_kst = 'TMath::Abs(H_MC_MOTHER_ID)  == 323'

        cut    = f'{tm_par} && {tm_psi} && {tm_kst}'
    #------------------------------------------------------------
    elif event_type == 'fail':
        cut= 'TMath::Abs(B_TRUEID) == 0 || TMath::Abs(Jpsi_TRUEID) == 0 || TMath::Abs(Jpsi_MC_MOTHER_ID) == 0 || TMath::Abs(L1_TRUEID) == 0 || TMath::Abs(L2_TRUEID) == 0 || TMath::Abs(L1_MC_MOTHER_ID) == 0 || TMath::Abs(L2_MC_MOTHER_ID) == 0 || TMath::Abs(H_TRUEID) == 0 || TMath::Abs(H_MC_MOTHER_ID) == 0'
    else:
        raise ValueError(f'Event type {event_type} not recognized')

    return cut
